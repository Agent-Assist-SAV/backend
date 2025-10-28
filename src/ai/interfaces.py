from abc import ABC, abstractmethod
from typing import AsyncGenerator
from src.chats.dtos import Chat


class IAIService(ABC):
    @abstractmethod
    async def suggest_response(self, chat: Chat) -> AsyncGenerator[str, None]:
        """Suggest a response based on the chat history and context."""
        pass