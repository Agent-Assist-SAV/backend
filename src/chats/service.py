from typing import Optional, AsyncGenerator
from uuid import uuid4
from src.chats.dtos import Chat, ChatMessage, ChatMessageRoleEnum, CreateChatMessageDTO
from src.ai.providers.ovh import OVHAIService
import asyncio


chats: list[Chat] = [Chat(id="1", messages=[
        ChatMessage(id="msg1", message="Hello!", role=ChatMessageRoleEnum.user),
        ChatMessage(id="msg2", message="How can I assist you today?", role=ChatMessageRoleEnum.assistant)
    ], context="General inquiry")]

# Queues SSE pour les messages
sse_queues_by_chat_id: dict[str, list[asyncio.Queue]] = {}

# Queues SSE pour les suggestions
suggestion_queues_by_chat_id: dict[str, list[asyncio.Queue]] = {}

# Instance du service IA (lazy loading)
_ai_service: Optional[OVHAIService] = None

def get_ai_service() -> OVHAIService:
    """Récupère l'instance du service IA (lazy loading)"""
    global _ai_service
    if _ai_service is None:
        _ai_service = OVHAIService()
    return _ai_service

# === Gestion SSE des messages ===

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
                print(f"Erreur lors de l'envoi du message SSE: {e}")

# === Gestion SSE des suggestions ===

def subscribe_to_suggestions_sse(chat_id: str) -> asyncio.Queue:
    """S'abonner au canal SSE des suggestions pour un chat"""
    if chat_id not in suggestion_queues_by_chat_id:
        suggestion_queues_by_chat_id[chat_id] = []
    queue: asyncio.Queue = asyncio.Queue()
    suggestion_queues_by_chat_id[chat_id].append(queue)
    return queue

def unsubscribe_from_suggestions_sse(chat_id: str, queue: asyncio.Queue) -> None:
    """Se désabonner du canal SSE des suggestions"""
    if chat_id in suggestion_queues_by_chat_id and queue in suggestion_queues_by_chat_id[chat_id]:
        suggestion_queues_by_chat_id[chat_id].remove(queue)
        if not suggestion_queues_by_chat_id[chat_id]:
            del suggestion_queues_by_chat_id[chat_id]

async def notify_suggestion_subscribers(chat_id: str, suggestion_chunk: str) -> None:
    """Envoyer un chunk de suggestion à tous les abonnés SSE"""
    if chat_id in suggestion_queues_by_chat_id:
        for queue in suggestion_queues_by_chat_id[chat_id]:
            try:
                await queue.put(suggestion_chunk)
            except Exception as e:
                print(f"Erreur lors de l'envoi de la suggestion SSE: {e}")

async def generate_and_stream_suggestion(chat_id: str) -> None:
    """
    Génère une suggestion et l'envoie aux abonnés SSE.
    Cette fonction est appelée automatiquement quand un message user est ajouté.
    """
    try:
        chat = get_chat_by_id(chat_id)
        if chat is None:
            return
        
        ai_service = get_ai_service()
        
        # Streamer chaque chunk de suggestion aux abonnés
        async for chunk in ai_service.suggest_response(chat):
            await notify_suggestion_subscribers(chat_id, chunk)
        
        # Envoyer un signal de fin
        await notify_suggestion_subscribers(chat_id, "[DONE]")
    except Exception as e:
        print(f"Erreur lors de la génération de suggestion: {e}")
        await notify_suggestion_subscribers(chat_id, "[ERROR]")

# === Opérations sur les chats ===

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
    
    # Notifier les subscribers des messages
    asyncio.create_task(notify_chat_subscribers(chat_id, new_message))
    
    # Si c'est un message utilisateur, générer automatiquement une suggestion
    if message_dto.role == ChatMessageRoleEnum.user:
        asyncio.create_task(generate_and_stream_suggestion(chat_id))
    
    return new_message

def update_chat_context(chat_id: str, context: str) -> None:
    chat = get_chat_by_id(chat_id)
    if chat is None:
        raise ValueError("Chat not found")
    chat.context = context