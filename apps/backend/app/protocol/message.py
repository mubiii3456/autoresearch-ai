from pydantic import BaseModel
from typing import Optional, Any
from enum import Enum


class MessageType(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"
    CLARIFICATION = "clarification"
    REJECTION = "rejection"


class AgentMessage(BaseModel):
    sender: str
    receiver: str
    message_type: MessageType
    payload: Any
    confidence_score: Optional[float] = None
    requires_clarification: bool = False
    clarification_question: Optional[str] = None