from fastapi import FastAPI
from pydantic import BaseModel
from app.graph.orchestrator import run_research

app = FastAPI(title="AutoResearch AI")


class ResearchRequest(BaseModel):
    query: str


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/research")
def research(request: ResearchRequest):
    result = run_research(request.query)

    if result.get("needs_clarification"):
        return {
            "status": "needs_clarification",
            "question": result["clarification_question"]
        }

    return {
        "status": "completed",
        "report": result.get("final_report"),
        "source": result["finding"].source if result.get("finding") else None
    }