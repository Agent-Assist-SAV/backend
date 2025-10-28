import os
import json
import httpx
from typing import AsyncGenerator
from src.ai.interfaces import IAIService
from src.chats.dtos import Chat


class OVHAIService(IAIService):
    """Service d'IA utilisant l'API Mistral 7B d'OVH"""
    
    def __init__(self):
        self.api_key = os.getenv("OVH_API_KEY")
        self.base_url = "https://mistral-7b-instruct-v0-3.endpoints.kepler.ai.cloud.ovh.net"
        if not self.api_key:
            raise ValueError("Missing OVH_API_KEY in environment variables")
    
    async def suggest_response(self, chat: Chat) -> AsyncGenerator[str, None]:
        messages = self._build_messages(chat)
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/openai_compat/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "messages": messages,
                    "stream": True,
                    "temperature": 0.7,
                    "max_tokens": 500
                }
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        
                        try:
                            chunk = json.loads(data)
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
    
    def _build_messages(self, chat: Chat) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        
        if chat.context:
            messages.append({
                "role": "system",
                "content": f"""Tu es un assistant SAV (Service Après-Vente) professionnel et empathique. 
Contexte de l'entreprise et/ou de l'assistance : {chat.context}

Ta mission est d'aider l'agent du SAV en suggérant des réponses appropriées, professionnelles et utiles basées sur la conversation.
Les réponses doivent être courtes, claires et directement utilisables par l'agent."""
            })
        else:
            messages.append({
                "role": "system",
                "content": """Tu es un assistant SAV (Service Après-Vente) professionnel et empathique.
Ta mission est d'aider l'agent du SAV en suggérant des réponses appropriées, professionnelles et utiles.
Les réponses doivent être courtes, claires et directement utilisables par l'agent."""
            })
        
        # Ajouter l'historique des messages
        for msg in chat.messages:
            messages.append({
                "role": msg.role.value,
                "content": msg.message
            })
        
        messages.append({
            "role": "system",
            "content": """Génère maintenant une suggestion de réponse que l'agent pourrait envoyer au client. 
IMPORTANT : 
- Ne fournis QUE le texte de la réponse suggérée, sans guillemets, sans explication, sans préambule
- Écris la réponse comme si tu étais directement l'agent qui parle au client
- Utilise une ponctuation correcte avec des espaces après les virgules, points, etc.
- Tu peux utiliser des retours à la ligne pour structurer la réponse si nécessaire
- Pas de placeholders, pas de formatage markdown (pas de **, pas de #, etc.), vraiment juste le texte brut avec une mise en forme simple si besoin
- Écris en français correct avec une grammaire et une orthographe parfaites"""
        })
        
        return messages
