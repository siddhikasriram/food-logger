from enum import StrEnum
from pathlib import Path
from typing import Protocol

from openai import OpenAI
from pydantic import BaseModel

from app.shared.exceptions import ServiceUnavailableError


PROMPT_PATH = Path(__file__).with_name("prompts") / "guardrail.md"


class InputCategory(StrEnum):
    FOOD = "food"
    WORKOUT = "workout"
    WATER = "water"
    OTHER = "other"


class InputClassification(BaseModel):
    category: InputCategory


class Guardrail(Protocol):
    def classify(self, message: str) -> InputClassification: ...


class OpenAIGuardrail:
    def __init__(self, api_key: str | None, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def classify(self, message: str) -> InputClassification:
        if not self.api_key:
            raise ServiceUnavailableError(
                "OpenAI is not configured. Set OPENAI_API_KEY on the backend."
            )

        try:
            response = OpenAI(api_key=self.api_key).responses.parse(
                model=self.model,
                instructions=PROMPT_PATH.read_text(encoding="utf-8").strip(),
                input=message,
                text_format=InputClassification,
                store=False,
            )
        except Exception as exc:
            raise ServiceUnavailableError(
                "The guardrail could not classify that message. Try again."
            ) from exc

        if response.output_parsed is None:
            raise ServiceUnavailableError(
                "The guardrail could not classify that message. Try again."
            )
        return response.output_parsed
