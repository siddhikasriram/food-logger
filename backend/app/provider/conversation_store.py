from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from threading import Lock
from time import monotonic
from uuid import uuid4

from app.schema.chat import ChatProposal, ChatStatus, ExtractedFood


@dataclass
class Conversation:
    conversation_id: str
    user_id: int
    consumed_at: datetime
    status: ChatStatus
    extracted_food: ExtractedFood
    proposal: ChatProposal | None = None
    touched_at: float = 0


class ConversationStore:
    """Process-local, expiring state for the chat workflow."""

    def __init__(
        self,
        ttl_seconds: int = 1800,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self.ttl_seconds = ttl_seconds
        self.clock = clock
        self._items: dict[str, Conversation] = {}
        self._lock = Lock()

    def create(
        self,
        *,
        user_id: int,
        consumed_at: datetime,
        status: ChatStatus,
        extracted_food: ExtractedFood,
        proposal: ChatProposal | None = None,
    ) -> Conversation:
        now = self.clock()
        conversation = Conversation(
            conversation_id=str(uuid4()),
            user_id=user_id,
            consumed_at=consumed_at,
            status=status,
            extracted_food=extracted_food,
            proposal=proposal,
            touched_at=now,
        )
        with self._lock:
            self._purge_expired(now)
            self._items[conversation.conversation_id] = conversation
        return conversation

    def get(self, conversation_id: str) -> Conversation | None:
        now = self.clock()
        with self._lock:
            self._purge_expired(now)
            conversation = self._items.get(conversation_id)
            if conversation is not None:
                conversation.touched_at = now
            return conversation

    def take(self, conversation_id: str) -> Conversation | None:
        now = self.clock()
        with self._lock:
            self._purge_expired(now)
            return self._items.pop(conversation_id, None)

    def put(self, conversation: Conversation) -> None:
        conversation.touched_at = self.clock()
        with self._lock:
            self._items[conversation.conversation_id] = conversation

    def delete(self, conversation_id: str) -> bool:
        with self._lock:
            return self._items.pop(conversation_id, None) is not None

    def clear(self) -> None:
        with self._lock:
            self._items.clear()

    def _purge_expired(self, now: float) -> None:
        expired = [
            key
            for key, value in self._items.items()
            if now - value.touched_at >= self.ttl_seconds
        ]
        for key in expired:
            del self._items[key]
