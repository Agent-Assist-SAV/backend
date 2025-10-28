from typing import Optional

from src.ai.interfaces import IAIService
from src.ai.providers.ovh import OVHAIService


_ai_service: Optional[IAIService] = None

def get_ai_service() -> IAIService:
    global _ai_service
    if _ai_service is None:
        _ai_service = OVHAIService()
    return _ai_service