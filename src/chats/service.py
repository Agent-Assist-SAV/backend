from typing import Optional
from uuid import uuid4
from src.chats.dtos import Chat, ChatMessage, ChatMessageRoleEnum, CreateChatMessageDTO
import asyncio

from src.dependencies import get_ai_service


chats: list[Chat] = [Chat(id="1", messages=[
        ChatMessage(id="msg1", message="Bonjour !", role=ChatMessageRoleEnum.user),
        ChatMessage(id="msg2", message="Comment puis-je vous aider aujourd'hui ?", role=ChatMessageRoleEnum.assistant)
    ], context="General inquiry")]

sse_queues_by_chat_id: dict[str, list[asyncio.Queue]] = {}

suggestion_queues_by_chat_id: dict[str, list[asyncio.Queue]] = {}

def subscribe_to_chat_sse(chat_id: str) -> asyncio.Queue:
    if chat_id not in sse_queues_by_chat_id:
        sse_queues_by_chat_id[chat_id] = []
    queue: asyncio.Queue = asyncio.Queue()
    sse_queues_by_chat_id[chat_id].append(queue)
    return queue

def unsubscribe_from_chat_sse(chat_id: str, queue: asyncio.Queue) -> None:
    if chat_id in sse_queues_by_chat_id and queue in sse_queues_by_chat_id[chat_id]:
        sse_queues_by_chat_id[chat_id].remove(queue)
        if not sse_queues_by_chat_id[chat_id]:
            del sse_queues_by_chat_id[chat_id]

async def notify_chat_subscribers(chat_id: str, message: ChatMessage) -> None:
    if chat_id in sse_queues_by_chat_id:
        for queue in sse_queues_by_chat_id[chat_id]:
            try:
                await queue.put(message)
            except Exception as e:
                print(f"Error when sending SSE message: {e}")


def subscribe_to_suggestions_sse(chat_id: str) -> asyncio.Queue:
    if chat_id not in suggestion_queues_by_chat_id:
        suggestion_queues_by_chat_id[chat_id] = []
    queue: asyncio.Queue = asyncio.Queue()
    suggestion_queues_by_chat_id[chat_id].append(queue)
    return queue

def unsubscribe_from_suggestions_sse(chat_id: str, queue: asyncio.Queue) -> None:
    if chat_id in suggestion_queues_by_chat_id and queue in suggestion_queues_by_chat_id[chat_id]:
        suggestion_queues_by_chat_id[chat_id].remove(queue)
        if not suggestion_queues_by_chat_id[chat_id]:
            del suggestion_queues_by_chat_id[chat_id]

async def notify_suggestion_subscribers(chat_id: str, suggestion_chunk: str) -> None:
    if chat_id in suggestion_queues_by_chat_id:
        for queue in suggestion_queues_by_chat_id[chat_id]:
            try:
                await queue.put(suggestion_chunk)
            except Exception as e:
                print(f"Error when sending suggestion SSE chunk: {e}")

async def generate_and_stream_suggestion(chat_id: str) -> None:
    try:
        chat = get_chat_by_id(chat_id)
        if chat is None:
            return
        
        ai_service = get_ai_service()
        
        async for chunk in ai_service.suggest_response(chat):
            await notify_suggestion_subscribers(chat_id, chunk)
        
        await notify_suggestion_subscribers(chat_id, "[DONE]")
    except Exception as e:
        print(f"Error during suggestion generation: {e}")
        await notify_suggestion_subscribers(chat_id, "[ERROR]")


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
    
    asyncio.create_task(notify_chat_subscribers(chat_id, new_message))
    
    if message_dto.role == ChatMessageRoleEnum.user:
        asyncio.create_task(generate_and_stream_suggestion(chat_id))
    
    return new_message

def update_chat_context(chat_id: str, context: str) -> None:
    chat = get_chat_by_id(chat_id)
    if chat is None:
        raise ValueError("Chat not found")
    chat.context = context