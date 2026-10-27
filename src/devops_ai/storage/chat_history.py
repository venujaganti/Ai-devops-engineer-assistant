"""Small bounded in-memory chat history store."""
from collections import deque

class ChatHistory:
    def __init__(self, max_messages: int = 30):
        if max_messages < 1:
            raise ValueError("max_messages must be positive")
        self._messages: deque[dict[str, str]] = deque(maxlen=max_messages)

    def add(self, role: str, content: str) -> None:
        if role not in {"user", "assistant", "system"}:
            raise ValueError("unsupported chat role")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("message content must not be empty")
        self._messages.append({"role": role, "content": content.strip()})

    def list_messages(self) -> list[dict[str, str]]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()
