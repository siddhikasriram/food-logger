from functools import lru_cache

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.provider.conversation_store import ConversationStore
from app.provider.guardrail import Guardrail, OpenAIGuardrail
from app.provider.meal_parser import MealAssistant, OpenAIMealAssistant
from app.schema.chat import (
    ChatCancelRequest,
    ChatCancelResponse,
    ChatConfirmRequest,
    ChatConfirmResponse,
    ChatMessageRequest,
    ChatMessageResponse,
)
from app.controller.chat import ChatController
from app.core.config import get_settings
from app.core.dependencies import db_session

router = APIRouter(prefix="/chat", tags=["chat"])


def get_guardrail() -> Guardrail:
    settings = get_settings()
    return OpenAIGuardrail(settings.openai_api_key, settings.openai_model)


def get_meal_assistant() -> MealAssistant:
    settings = get_settings()
    return OpenAIMealAssistant(settings.openai_api_key, settings.openai_model)


@lru_cache
def get_conversation_store() -> ConversationStore:
    return ConversationStore(get_settings().chat_conversation_ttl_seconds)


def get_chat_controller(
    db: Session = Depends(db_session),
    guardrail: Guardrail = Depends(get_guardrail),
    assistant: MealAssistant = Depends(get_meal_assistant),
    conversations: ConversationStore = Depends(get_conversation_store),
) -> ChatController:
    return ChatController(db, guardrail, assistant, conversations)


@router.post("/messages", response_model=ChatMessageResponse)
def create_message(
    payload: ChatMessageRequest,
    controller: ChatController = Depends(get_chat_controller),
) -> ChatMessageResponse:
    return controller.message(payload)


@router.post("/confirm", response_model=ChatConfirmResponse)
def confirm_meal(
    payload: ChatConfirmRequest,
    controller: ChatController = Depends(get_chat_controller),
) -> ChatConfirmResponse:
    return controller.confirm(payload.conversation_id)


@router.post("/cancel", response_model=ChatCancelResponse)
def cancel_conversation(
    payload: ChatCancelRequest,
    controller: ChatController = Depends(get_chat_controller),
) -> ChatCancelResponse:
    return controller.cancel(payload.conversation_id)
