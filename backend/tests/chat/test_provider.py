from types import SimpleNamespace

import pytest

from app.provider.meal_parser import OpenAIMealAssistant
from app.shared.exceptions import ServiceUnavailableError


def test_missing_api_key_is_reported() -> None:
    with pytest.raises(ServiceUnavailableError, match="OPENAI_API_KEY"):
        OpenAIMealAssistant(None, "test-model").extract_food("lunch")


def test_empty_structured_response_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResponses:
        def parse(self, **_kwargs):
            return SimpleNamespace(output_parsed=None)

    class FakeOpenAI:
        def __init__(self, **_kwargs) -> None:
            self.responses = FakeResponses()

    monkeypatch.setattr("app.provider.meal_parser.OpenAI", FakeOpenAI)

    with pytest.raises(ServiceUnavailableError, match="extract"):
        OpenAIMealAssistant("test-key", "test-model").extract_food("lunch")
