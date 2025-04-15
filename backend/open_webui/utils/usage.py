import json
import logging
import time
import uuid
from decimal import Decimal
from typing import List, Union, Optional

import tiktoken
from fastapi import HTTPException
from openai.types import CompletionUsage
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from pydantic import BaseModel, ConfigDict, Field
from tiktoken import Encoding

from open_webui.config import (
    USAGE_CALCULATE_DEFAULT_TOKEN_PRICE,
    USAGE_CALCULATE_DEFAULT_REQUEST_PRICE,
    USAGE_CALCULATE_MODEL_PREFIX_TO_REMOVE,
    USAGE_DEFAULT_ENCODING_MODEL,
)
from open_webui.env import SRC_LOG_LEVELS
from open_webui.models.credits import AddCreditForm, Credits, SetCreditFormDetail
from open_webui.models.models import ModelModel, Models
from open_webui.models.users import UserModel

logger = logging.getLogger(__name__)
logger.setLevel(SRC_LOG_LEVELS["MAIN"])


class FileFile(BaseModel):
    model_config = ConfigDict(extra="allow")

    file_data: Optional[str] = Field(default="")
    file_id: Optional[str] = Field(default="")
    filename: Optional[str] = Field(default="")


class InputAudio(BaseModel):
    model_config = ConfigDict(extra="allow")

    data: Optional[str] = Field(default="")
    format: Optional[str] = Field(default="")


class ImageURL(BaseModel):
    model_config = ConfigDict(extra="allow")

    url: Optional[str] = Field(default="")
    detail: Optional[str] = Field(default="")


class MessageContent(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: Optional[str] = Field(default="")
    text: Optional[str] = Field(default="")
    image_url: Optional[ImageURL] = Field(default_factory=lambda: ImageURL())
    input_audio: Optional[InputAudio] = Field(default_factory=lambda: InputAudio())
    file: Optional[FileFile] = Field(default_factory=lambda: FileFile())


class MessageItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    role: str
    content: Union[str, list[MessageContent]] = Field(default="")


class Calculator:
    """
    Usage Calculator
    """

    def __init__(self) -> None:
        self._encoder = {}

    def get_encoder(
        self,
        model_id: str,
        model_prefix_to_remove: str = "",
        default_model_for_encoding: str = "gpt-4o",
    ) -> Encoding:
        # remove prefix
        model_id_ops = model_id
        if model_prefix_to_remove:
            model_id_ops = model_id.lstrip(model_prefix_to_remove)
        # load from cache
        if model_id_ops in self._encoder:
            return self._encoder[model_id_ops]
        # load from tiktoken
        try:
            self._encoder[model_id_ops] = tiktoken.encoding_for_model(model_id_ops)
        except KeyError:
            return self.get_encoder(default_model_for_encoding)
        return self.get_encoder(model_id)

    def get_message_content(self, content: Union[str, list[MessageContent]]):
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "".join(
                [
                    item.model_dump_json(exclude_none=True, exclude_unset=True)
                    for item in content
                ]
            )
        return str(content)

    def calculate_usage(
        self,
        cached_usage: CompletionUsage,
        model_id: str,
        messages: List[dict],
        response: Union[ChatCompletion, ChatCompletionChunk],
        model_prefix_to_remove: str = "",
        default_model_for_encoding: str = "gpt-4o",
    ) -> (bool, CompletionUsage):
        try:
            # use provider usage
            if response.usage is not None:
                return True, response.usage

            # init
            usage = CompletionUsage(
                prompt_tokens=0, completion_tokens=0, total_tokens=0
            )
            encoder = self.get_encoder(
                model_id=model_id,
                model_prefix_to_remove=model_prefix_to_remove,
                default_model_for_encoding=default_model_for_encoding,
            )

            # prompt tokens
            # only calculate once
            if cached_usage.prompt_tokens:
                usage.prompt_tokens = cached_usage.prompt_tokens
            else:
                usage.prompt_tokens += sum(
                    len(encoder.encode(self.get_message_content(message.content) or ""))
                    for message in [
                        MessageItem.model_validate(message) for message in messages
                    ]
                )

            # completion tokens
            choices = response.choices
            if choices:
                choice = choices[0]
                if isinstance(response, ChatCompletion):
                    usage.completion_tokens = len(
                        encoder.encode(choice.message.content or "")
                    )
                elif isinstance(response, ChatCompletionChunk):
                    usage.completion_tokens = len(
                        encoder.encode(choice.delta.content or "")
                    )

            # total tokens
            usage.total_tokens = usage.prompt_tokens + usage.completion_tokens
            return False, usage
        except Exception as err:
            logger.exception("[calculate_usage] failed: %s", err)
            raise err


calculator = Calculator()


class CreditDeduct:
    """
    Deduct Credit

    Must be used as following, so __exit__ will be called on exit

    with CreditDeduct(xxx) as credit_deduct:
        credit_deduct.run(xxx)
    """

    def __init__(
        self,
        user: UserModel,
        model_id: str,
        body: dict,
        is_stream: bool,
    ) -> None:
        self.user = user
        self.model_id = model_id
        self.model = Models.get_model_by_id(self.model_id)
        self.body = body
        self.is_stream = is_stream
        self.usage = CompletionUsage(
            prompt_tokens=0, completion_tokens=0, total_tokens=0
        )
        self.prompt_unit_price, self.completion_unit_price, self.request_unit_price = (
            self.get_model_price()
        )
        self.is_official_usage = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        Credits.add_credit_by_user_id(
            form_data=AddCreditForm(
                user_id=self.user.id,
                amount=Decimal(-self.total_price),
                detail=SetCreditFormDetail(
                    usage={
                        "prompt_unit_price": float(self.prompt_unit_price),
                        "completion_unit_price": float(self.completion_unit_price),
                        "request_unit_price": float(self.request_unit_price),
                        **self.usage.model_dump(exclude_unset=True, exclude_none=True),
                    },
                    api_params={
                        "model": (
                            self.model.model_dump(exclude_unset=True, exclude_none=True)
                            if self.model
                            else {"id": self.model_id}
                        ),
                        "is_stream": self.is_stream,
                    },
                    desc=f"updated by {self.__class__.__name__}",
                ),
            )
        )
        logger.info(
            "[credit_deduct] user: %s; tokens: %d %d; cost: %s",
            self.user.id,
            self.usage.prompt_tokens,
            self.usage.completion_tokens,
            self.total_price,
        )

    @property
    def prompt_price(self) -> Decimal:
        return self.prompt_unit_price * self.usage.prompt_tokens / 1000 / 1000

    @property
    def completion_price(self) -> Decimal:
        return self.completion_unit_price * self.usage.completion_tokens / 1000 / 1000

    @property
    def request_price(self) -> Decimal:
        return self.request_unit_price / 1000 / 1000

    @property
    def total_price(self) -> Decimal:
        if self.request_unit_price > 0:
            return self.request_price
        return self.prompt_price + self.completion_price

    @property
    def usage_with_cost(self) -> dict:
        return {
            "total_cost": float(self.total_price),
            "cost_detail": {
                "prompt_price": float(self.prompt_price),
                "completion_price": float(self.completion_price),
                "request_price": float(self.request_price),
                "is_calculate": not self.is_official_usage,
            },
            **self.usage.model_dump(exclude_unset=True, exclude_none=True),
        }

    def get_model_price(self) -> (Decimal, Decimal, Decimal):
        if self.model is None or not isinstance(self.model, ModelModel):
            return (
                Decimal(USAGE_CALCULATE_DEFAULT_TOKEN_PRICE.value),
                Decimal(USAGE_CALCULATE_DEFAULT_TOKEN_PRICE.value),
                Decimal(USAGE_CALCULATE_DEFAULT_REQUEST_PRICE.value),
            )
        model_price = self.model.price or {}
        return (
            Decimal(
                model_price.get(
                    "prompt_price", USAGE_CALCULATE_DEFAULT_TOKEN_PRICE.value
                )
            ),
            Decimal(
                model_price.get(
                    "completion_price", USAGE_CALCULATE_DEFAULT_TOKEN_PRICE.value
                )
            ),
            Decimal(
                model_price.get(
                    "request_price", USAGE_CALCULATE_DEFAULT_REQUEST_PRICE.value
                )
            ),
        )

    def run(self, response: Union[dict, bytes, str]) -> None:
        try:
            self._run(response)
        except Exception as e:
            logger.warning("[credit_deduct_failed] unknown error %s", e)

    def _run(self, response: Union[dict, bytes, str]) -> None:
        if not isinstance(response, (dict, bytes, str)):
            logger.warning("[credit_deduct] response is type of %s", type(response))
            return

        # prompt messages
        messages = self.body.get("messages", [])
        if not messages:
            raise HTTPException(status_code=400, detail="prompt messages is empty")

        # stream
        if self.is_stream:
            _response = self.clean_response(
                response=response,
                default_response={
                    "id": uuid.uuid4().hex,
                    "choices": [{"delta": {"content": str(response)}, "index": 0}],
                    "created": int(time.time()),
                    "model": self.model_id,
                    "object": "chat.completion.chunk",
                },
            )
            if not _response:
                return
            # validate
            _response["object"] = "chat.completion.chunk"
            response = ChatCompletionChunk.model_validate(_response)

        # non-stream
        else:
            _response = self.clean_response(
                response=response,
                default_response={
                    "id": uuid.uuid4().hex,
                    "choices": [{"message": {"content": str(response)}, "index": 0}],
                    "created": int(time.time()),
                    "model": self.model_id,
                    "object": "chat.completion",
                },
            )
            if not _response:
                return
            # validate
            response["object"] = "chat.completion"
            response = ChatCompletion.model_validate(_response)

        # calculate
        is_official_usage, usage = calculator.calculate_usage(
            cached_usage=self.usage,
            model_id=self.model_id,
            messages=messages,
            response=response,
            model_prefix_to_remove=USAGE_CALCULATE_MODEL_PREFIX_TO_REMOVE.value,
            default_model_for_encoding=USAGE_DEFAULT_ENCODING_MODEL.value,
        )
        if is_official_usage:
            self.is_official_usage = True
            self.usage = usage
            return
        if self.is_official_usage:
            return
        if self.is_stream:
            self.usage.prompt_tokens = usage.prompt_tokens
            self.usage.completion_tokens += usage.completion_tokens
            self.usage.total_tokens = (
                self.usage.prompt_tokens + self.usage.completion_tokens
            )
            return
        self.usage = usage

    def clean_response(
        self, response: Union[dict, bytes, str], default_response: dict
    ) -> dict:
        # dict
        if isinstance(response, dict):
            return response
        # str or bytes
        if isinstance(response, bytes):
            _response = response.decode("utf-8")
        else:
            _response = response
        # remove prefix
        _response = _response.strip().lstrip("data: ")
        if _response.startswith("[DONE]"):
            return {}
        try:
            _response = json.loads(_response)
        except json.decoder.JSONDecodeError:
            _response = default_response
        return _response
