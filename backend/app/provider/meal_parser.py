import json
from pathlib import Path
from typing import Protocol

from openai import OpenAI

from app.schema.chat import (
    ExtractedFood,
    ExtractedIngredients,
)
from app.shared.exceptions import ServiceUnavailableError

PROMPT_DIRECTORY = Path(__file__).with_name("prompts")


class MealAssistant(Protocol):
    def extract_food(self, message: str) -> ExtractedFood: ...

    def extract_ingredients(
        self, message: str, catalog: dict[str, object]
    ) -> ExtractedIngredients: ...


class OpenAIMealAssistant:
    def __init__(self, api_key: str | None, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def extract_food(self, message: str) -> ExtractedFood:
        return self._parse(
            prompt_name="meal_parser.md",
            message=message,
            text_format=ExtractedFood,
            failure_message="The meal assistant could not extract that food. Try again.",
        )

    def extract_ingredients(
        self, message: str, catalog: dict[str, object]
    ) -> ExtractedIngredients:
        return self._parse(
            prompt_name="ingredient_parser.md",
            message=message,
            text_format=ExtractedIngredients,
            failure_message="The meal assistant could not extract those ingredients. Try again.",
            catalog=catalog,
        )

    def _parse(self, *, prompt_name, message, text_format, failure_message, catalog=None):
        if not self.api_key:
            raise ServiceUnavailableError(
                "OpenAI is not configured. Set OPENAI_API_KEY on the backend."
            )

        instructions = (PROMPT_DIRECTORY / prompt_name).read_text(encoding="utf-8")
        if catalog is not None:
            instructions = instructions.replace(
                "{{CATALOG}}", json.dumps(catalog, separators=(",", ":"))
            )

        try:
            response = OpenAI(api_key=self.api_key).responses.parse(
                model=self.model,
                instructions=instructions.strip(),
                input=message,
                text_format=text_format,
                store=False,
            )
        except Exception as exc:
            raise ServiceUnavailableError(failure_message) from exc

        if response.output_parsed is None:
            raise ServiceUnavailableError(failure_message)
        return response.output_parsed
