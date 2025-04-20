from decimal import Decimal
from typing import Optional, Union

from fastapi import HTTPException

from open_webui.config import (
    USAGE_CALCULATE_FEATURE_IMAGE_GEN_PRICE,
    USAGE_CALCULATE_FEATURE_CODE_EXECUTE_PRICE,
    USAGE_CALCULATE_FEATURE_WEB_SEARCH_PRICE,
    USAGE_CALCULATE_FEATURE_TOOL_SERVER_PRICE,
    USAGE_CALCULATE_DEFAULT_TOKEN_PRICE,
    USAGE_CALCULATE_DEFAULT_REQUEST_PRICE,
    CREDIT_NO_CREDIT_MSG,
)
from open_webui.models.chats import Chats
from open_webui.models.credits import Credits
from open_webui.models.models import Models, ModelModel


def get_model_price(model: Optional[ModelModel] = None) -> (Decimal, Decimal, Decimal):
    # no model provide
    if not model or not isinstance(model, ModelModel):
        return (
            Decimal(USAGE_CALCULATE_DEFAULT_TOKEN_PRICE.value),
            Decimal(USAGE_CALCULATE_DEFAULT_TOKEN_PRICE.value),
            Decimal(USAGE_CALCULATE_DEFAULT_REQUEST_PRICE.value),
        )
    # base model
    if model.base_model_id:
        base_model = Models.get_model_by_id(model.base_model_id)
        if base_model:
            return get_model_price(base_model)
    # model price
    model_price = model.price or {}
    return (
        Decimal(
            model_price.get("prompt_price", USAGE_CALCULATE_DEFAULT_TOKEN_PRICE.value)
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


def get_feature_price(features: Union[set, list]) -> Decimal:
    if not features:
        return Decimal(0)
    price = Decimal(0)
    for feature in features:
        match feature:
            case "image_generation":
                price += (
                    Decimal(USAGE_CALCULATE_FEATURE_IMAGE_GEN_PRICE.value) / 1000 / 1000
                )
            case "code_interpreter":
                price += (
                    Decimal(USAGE_CALCULATE_FEATURE_CODE_EXECUTE_PRICE.value)
                    / 1000
                    / 1000
                )
            case "web_search":
                price += (
                    Decimal(USAGE_CALCULATE_FEATURE_WEB_SEARCH_PRICE.value)
                    / 1000
                    / 1000
                )
            case "direct_tool_servers":
                price += (
                    Decimal(USAGE_CALCULATE_FEATURE_TOOL_SERVER_PRICE.value)
                    / 1000
                    / 1000
                )
    return price


def is_free_request(form_data: dict) -> bool:
    model_id = form_data.get("model") or form_data.get("model_id") or ""
    model_price = get_model_price(Models.get_model_by_id(model_id))
    is_free_model = sum(float(price) for price in model_price) <= 0

    features = (
        form_data.get("features")
        or (form_data.get("metadata") or {}).get("features")
        or {}
    )
    is_feature_free = get_feature_price({k for k, v in features.items() if v}) <= 0

    return is_free_model and is_feature_free


def check_credit_by_user_id(user_id: str, form_data: dict) -> None:
    # check for free
    if is_free_request(form_data):
        return
    # check for credit
    metadata = form_data.get("metadata") or form_data
    credit = Credits.init_credit_by_user_id(user_id=user_id)
    if credit is None or credit.credit <= 0:
        if isinstance(metadata, dict) and metadata:
            chat_id = metadata.get("chat_id")
            message_id = metadata.get("message_id") or metadata.get("id")
            if chat_id and message_id:
                Chats.upsert_message_to_chat_by_id_and_message_id(
                    chat_id,
                    message_id,
                    {"error": {"content": CREDIT_NO_CREDIT_MSG.value}},
                )
        raise HTTPException(status_code=403, detail=CREDIT_NO_CREDIT_MSG.value)
