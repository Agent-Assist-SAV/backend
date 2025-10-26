from typing import Optional
from uuid import uuid4
from src.chats.dtos import Chat, ChatMessage, ChatMessageRoleEnum, CreateChatMessageDTO


chats: list[Chat] = [Chat(id="1", messages=[
        ChatMessage(id="msg1", message="Hello!", role=ChatMessageRoleEnum.user),
        ChatMessage(id="msg2", message="How can I assist you today?", role=ChatMessageRoleEnum.assistant)
    ], context="General inquiry")]

def get_chats() -> list[Chat]:
    return chats

def create_chat() -> Chat:
    new_chat = Chat(id=uuid4().hex, messages=[], context="")
    chats.append(new_chat)
    return new_chat

def get_chat_by_id(chat_id: str) -> Optional[Chat]:
    return next((c for c in chats if c.id == chat_id), None)

def add_message_to_chat(chat_id: str, message_dto: CreateChatMessageDTO) -> ChatMessage:
    chat = get_chat_by_id(chat_id)
    if chat is None:
        raise ValueError("Chat not found")
    new_message = ChatMessage(id=uuid4().hex, message=message_dto.message, role=message_dto.role)
    chat.messages.append(new_message)
    return new_message

def update_chat_context(chat_id: str, context: str) -> None:
    chat = get_chat_by_id(chat_id)
    if chat is None:
        raise ValueError("Chat not found")
    chat.context = context