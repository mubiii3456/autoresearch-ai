from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
import queue
import threading
from app.graph.orchestrator import run_research
from fastapi import WebSocket
from app.graph.orchestrator import app as research_graph, build_initial_state, STEP_LABELS
from app.mcp_clients.storage_client import list_reports, get_report
from app.graph.orchestrator import run_until_critic, run_writer_editor

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
        "source": result["finding"].source if result.get("finding") else None,
        "tokens": result.get("total_tokens"),
        "cost": result.get("total_cost")
    }

@app.websocket("/ws/research")
async def websocket_research(websocket: WebSocket):
    await websocket.accept()

    data = await websocket.receive_json()
    query = data["query"]

    state = await asyncio.to_thread(run_until_critic, query)

    if state["needs_clarification"]:
        await websocket.send_json({
            "type": "final",
            "status": "needs_clarification",
            "question": state["clarification_question"]
        })
        await websocket.close()
        return

    if not state["feedback"].approved:
        await websocket.send_json({
            "type": "final",
            "status": "max_retries",
            "message": "Could not verify a claim after multiple attempts."
        })
        await websocket.close()
        return

    await websocket.send_json({
        "type": "approval_needed",
        "claim": state["finding"].claim,
        "source": state["finding"].source
    })

    try:
        approval_response = await websocket.receive_json()
    except Exception:
        return

    if not approval_response.get("approved"):
        await websocket.send_json({
            "type": "final",
            "status": "rejected_by_user",
            "message": "Report generation cancelled by user."
        })
        await websocket.close()
        return

    final_state = await asyncio.to_thread(run_writer_editor, state)

    await websocket.send_json({
        "type": "final",
        "status": "completed",
        "report": final_state.get("final_report"),
        "source": final_state["finding"].source,
        "tokens": final_state.get("total_tokens"),
        "cost": final_state.get("total_cost")
    })

    await websocket.close()

@app.get("/reports")
def get_all_reports():
    return list_reports()


@app.get("/reports/{report_id}")
def get_single_report(report_id: str):
    return get_report(report_id)