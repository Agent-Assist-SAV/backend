from typing import Optional
from uuid import uuid4
from src.chats.dtos import Chat, ChatMessage, ChatMessageRoleEnum, CreateChatMessageDTO
import asyncio


chats: list[Chat] = [Chat(id="1", messages=[
        ChatMessage(id="msg1", message="Hello!", role=ChatMessageRoleEnum.user),
        ChatMessage(id="msg2", message="How can I assist you today?", role=ChatMessageRoleEnum.assistant)
    ], context="General inquiry")]

# Dictionnaire pour stocker les queues SSE par chat_id
# Format: {chat_id: [queue1, queue2, ...]}
sse_queues: dict[str, list] = {}

def subscribe_to_chat_sse(chat_id: str) -> asyncio.Queue:
    """S'abonner aux messages SSE d'un chat"""
    if chat_id not in sse_queues:
        sse_queues[chat_id] = []
    queue: asyncio.Queue = asyncio.Queue()
    sse_queues[chat_id].append(queue)
    return queue

def unsubscribe_from_chat_sse(chat_id: str, queue: asyncio.Queue) -> None:
    """Se désabonner des messages SSE d'un chat"""
    if chat_id in sse_queues and queue in sse_queues[chat_id]:
        sse_queues[chat_id].remove(queue)
        if not sse_queues[chat_id]:
            del sse_queues[chat_id]

async def notify_chat_subscribers(chat_id: str, message: ChatMessage) -> None:
    """Notifier tous les subscribers d'un chat avec un nouveau message"""
    if chat_id in sse_queues:
        for queue in sse_queues[chat_id]:
            try:
                await queue.put(message)
            except Exception as e:
                print(f"Erreur lors de l'envoi du message SSE: {e}")

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
    # Notifier les subscribers
    asyncio.create_task(notify_chat_subscribers(chat_id, new_message))
    return new_message

def update_chat_context(chat_id: str, context: str) -> None:
    chat = get_chat_by_id(chat_id)
    if chat is None:
        raise ValueError("Chat not found")
    chat.context = context