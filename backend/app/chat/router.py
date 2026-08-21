from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.chat.provider import MealParser, OpenAIMealParser
from app.chat.schemas import (
    ChatConfirmRequest,
    ChatConfirmResponse,
    ChatMessageRequest,
    ChatMessageResponse,
)
from app.chat.service import ChatService
from app.core.config import get_settings
from app.core.dependencies import db_session

router = APIRouter(prefix="/chat", tags=["chat"])


def get_meal_parser() -> MealParser:
    settings = get_settings()
    return OpenAIMealParser(settings.openai_api_key, settings.openai_model)


def get_chat_service(
    db: Session = Depends(db_session),
    parser: MealParser = Depends(get_meal_parser),
) -> ChatService:
    return ChatService(db, parser)


@router.post("/messages", response_model=ChatMessageResponse)
def create_message(
    payload: ChatMessageRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatMessageResponse:
    return service.propose(payload)


@router.post("/confirm", response_model=ChatConfirmResponse)
def confirm_meal(
    payload: ChatConfirmRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatConfirmResponse:
    return service.confirm(payload.proposal)
