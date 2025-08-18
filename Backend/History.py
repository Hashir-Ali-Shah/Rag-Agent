from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage

class BufferWindowMessageHistory(BaseChatMessageHistory):
    def __init__(self, k: int = 4):
        # Initialize message list and window size
        self.messages: list[BaseMessage] = []
        self.k = k

    def add_messages(self, messages: list[BaseMessage]) -> None:
        """Add new messages and keep only the last `k`."""
        self.messages.extend(messages)
        self.messages = self.messages[-self.k:]

    def clear(self) -> None:
        """Clear the history."""
        self.messages = []
