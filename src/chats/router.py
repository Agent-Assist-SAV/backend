from typing import Optional
from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse

from src.chats.dtos import Chat, ChatMessage, CreateChatMessageDTO
import src.chats.service as service

router = APIRouter(tags=["chats"])

@router.get("/chats")
async def get_chats() -> list[Chat]:
    return service.get_chats()

@router.post("/chats")
async def create_chat() -> Chat:
    return service.create_chat()

@router.get("/chats/{chat_id}")
async def get_chat(chat_id: str) -> Optional[Chat]:
    return service.get_chat_by_id(chat_id)

@router.post("/chats/{chat_id}/messages")
async def add_message_to_chat(chat_id: str, message: CreateChatMessageDTO) -> ChatMessage:
    return service.add_message_to_chat(chat_id, message)

@router.get("/chats/{chat_id}/sse")
async def chat_sse(chat_id: str):
    async def message_generator():
        queue = service.subscribe_to_chat_sse(chat_id)
        try:
            while True:
                message = await queue.get()
                # Envoyer le message en format SSE
                yield f"data: {message.model_dump_json()}\n\n"
        except Exception as e:
            print(f"Erreur SSE: {e}")
        finally:
            service.unsubscribe_from_chat_sse(chat_id, queue)
    
    return StreamingResponse(message_generator(), media_type="text/event-stream")

@router.get("/chats/{chat_id}/suggest")
async def chat_suggest_sse(chat_id: str):
    async def suggestion_generator():
        queue = service.subscribe_to_suggestions_sse(chat_id)
        try:
            while True:
                chunk = await queue.get()
                
                if chunk == "[DONE]":
                    yield "data: [DONE]\n\n"
                    break
                
                if chunk == "[ERROR]":
                    yield "event: error\ndata: Erreur lors de la génération\n\n"
                    break
                
                yield f"data: {chunk}\n\n"
        except Exception as e:
            print(f"Erreur SSE suggestion: {e}")
            yield f"event: error\ndata: {str(e)}\n\n"
        finally:
            service.unsubscribe_from_suggestions_sse(chat_id, queue)
    
    return StreamingResponse(
        suggestion_generator(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )

@router.put("/chats/{chat_id}/context")
async def update_chat_context(chat_id: str, context: str = Body(...)) -> None:
    service.update_chat_context(chat_id, context) 