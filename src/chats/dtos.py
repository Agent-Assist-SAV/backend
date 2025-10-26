from enum import Enum
from pydantic import BaseModel


class ChatMessageRoleEnum(str, Enum):
    user = "user"
    assistant = "assistant"

class ChatMessage(BaseModel):
    id: str
    message: str
    role: ChatMessageRoleEnum

class Chat(BaseModel):
    id: str
    messages: list[ChatMessage]

class CreateChatMessageDTO(BaseModel):
    message: str
    role: ChatMessageRoleEnum