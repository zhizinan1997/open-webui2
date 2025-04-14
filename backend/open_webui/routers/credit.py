import datetime
import logging
import uuid

from fastapi import APIRouter, Depends, Request
from fastapi.responses import PlainTextResponse

from open_webui.env import SRC_LOG_LEVELS
from open_webui.models.credits import TradeTicketModel, TradeTickets
from open_webui.models.users import UserModel
from open_webui.utils.auth import get_current_user
from open_webui.utils.credit.ezfp import ezfp_client

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MAIN"])

router = APIRouter()


@router.post("/tickets", response_model=TradeTicketModel)
async def create_ticket(
    request: Request, form_data: dict, user: UserModel = Depends(get_current_user)
) -> TradeTicketModel:
    out_trade_no = (
        f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.{uuid.uuid4().hex}"
    )
    return TradeTickets.insert_new_ticket(
        id=out_trade_no,
        user_id=user.id,
        amount=form_data["amount"],
        detail=await ezfp_client.create_trade(
            pay_type=form_data["pay_type"],
            out_trade_no=out_trade_no,
            amount=form_data["amount"],
            client_ip=request.client.host,
            ua=request.headers.get("User-Agent"),
        ),
    )


@router.post("/callback", response_class=PlainTextResponse)
async def ticket_callback(request: Request) -> str:
    if not ezfp_client.verify(request.query_params):
        return "invalid signature"

    # payment failed
    if request.query_params["trade_status"] != "TRADE_SUCCESS":
        return "success"

    # find ticket
    ticket = TradeTickets.get_ticket_by_id(request.query_params["out_trade_no"])
    if not ticket:
        return "no ticket fount"

    # already callback
    if ticket.detail.get("callback"):
        return "success"

    ticket.detail["callback"] = dict(request.query_params)
    TradeTickets.update_credit_by_id(ticket.id, ticket.detail)

    return "success"
