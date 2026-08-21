from types import SimpleNamespace

import pytest

from app.chat.provider import OpenAIMealParser
from app.shared.exceptions import ServiceUnavailableError


def test_missing_api_key_is_reported() -> None:
    with pytest.raises(ServiceUnavailableError, match="OPENAI_API_KEY"):
        OpenAIMealParser(None, "test-model").parse("lunch", {})


def test_empty_structured_response_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResponses:
        def parse(self, **_kwargs):
            return SimpleNamespace(output_parsed=None)

    class FakeOpenAI:
        def __init__(self, **_kwargs) -> None:
            self.responses = FakeResponses()

    monkeypatch.setattr("app.chat.provider.OpenAI", FakeOpenAI)

    with pytest.raises(ServiceUnavailableError, match="usable recipe"):
        OpenAIMealParser("test-key", "test-model").parse("lunch", {})
