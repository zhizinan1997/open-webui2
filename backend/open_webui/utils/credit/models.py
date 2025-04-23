from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import List, Union, Optional


class CompletionTokensDetails(BaseModel):
    model_config = ConfigDict(extra="allow")
    accepted_prediction_tokens: Optional[int] = None
    audio_tokens: Optional[int] = None
    reasoning_tokens: Optional[int] = None
    rejected_prediction_tokens: Optional[int] = None


class PromptTokensDetails(BaseModel):
    model_config = ConfigDict(extra="allow")
    audio_tokens: Optional[int] = None
    cached_tokens: Optional[int] = None


class CompletionUsage(BaseModel):
    model_config = ConfigDict(extra="allow")
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int
    completion_tokens_details: Optional[CompletionTokensDetails] = None
    prompt_tokens_details: Optional[PromptTokensDetails] = None

    @model_validator(mode="before")
    @classmethod
    def format_input(cls, data: dict) -> dict:
        if not isinstance(data, dict):
            return data
        # format gemini usage
        if "promptTokenCount" in data:
            data.update(
                {
                    "prompt_tokens": data.pop("promptTokenCount"),
                    "completion_tokens": data.pop("candidatesTokenCount"),
                    "total_tokens": data.pop("totalTokenCount"),
                }
            )
        # format claude usage
        elif "input_tokens" in data:
            data.update(
                {
                    "prompt_tokens": data.pop("input_tokens"),
                    "completion_tokens": data.pop("output_tokens"),
                }
            )
            data["total_tokens"] = data.pop(
                "total_tokens", data["prompt_tokens"] + data["completion_tokens"]
            )
        return data


class ChatCompletionMessage(BaseModel):
    model_config = ConfigDict(extra="allow")
    content: Optional[str] = None


class ChoiceDelta(BaseModel):
    model_config = ConfigDict(extra="allow")
    content: Optional[str] = None


class Choice(BaseModel):
    model_config = ConfigDict(extra="allow")
    message: Optional[ChatCompletionMessage] = Field(
        default_factory=lambda: ChatCompletionMessage()
    )
    delta: Optional[ChoiceDelta] = Field(default_factory=lambda: ChoiceDelta())


class ChatCompletion(BaseModel):
    model_config = ConfigDict(extra="allow")
    choices: List[Choice] = Field(default_factory=lambda: [])
    usage: Optional[CompletionUsage] = None


class ChatCompletionChunk(BaseModel):
    model_config = ConfigDict(extra="allow")
    choices: List[Choice] = Field(default_factory=lambda: [])
    usage: Optional[CompletionUsage] = None


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
