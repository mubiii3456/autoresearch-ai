from pydantic import BaseModel, Field


class ResearchFinding(BaseModel):
    claim: str
    source: str
    confidence: float = Field(ge=0, le=1)


class CriticFeedback(BaseModel):
    approved: bool
    reason: str