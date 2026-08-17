from typing import TypedDict, Optional, List
from app.schemas.models import ResearchFinding, CriticFeedback


class AgentState(TypedDict):
    query: str
    finding: Optional[ResearchFinding]
    feedback: Optional[CriticFeedback]
    attempts: int
    rejected_claims: List[str]
    verified_findings: List[ResearchFinding]
    needs_clarification: bool
    clarification_question: Optional[str]