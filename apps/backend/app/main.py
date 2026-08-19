from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
import queue
import threading
from app.graph.orchestrator import run_research
from fastapi import WebSocket
from app.graph.orchestrator import app as research_graph, build_initial_state, STEP_LABELS
from app.mcp_clients.storage_client import list_reports, get_report

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

    initial_state = build_initial_state(query)
    event_queue = queue.Queue()

    def run_graph():
        for event in research_graph.stream(initial_state):
            event_queue.put(event)
        event_queue.put(None)

    thread = threading.Thread(target=run_graph)
    thread.start()

    final_state = None

    while True:
        event = await asyncio.to_thread(event_queue.get)

        if event is None:
            break

        for node_name, node_state in event.items():
            label = STEP_LABELS.get(node_name, f"{node_name} running...")
            await websocket.send_json({"type": "step", "message": label})
            final_state = node_state

    thread.join()

    if final_state.get("needs_clarification"):
        await websocket.send_json({
            "type": "final",
            "status": "needs_clarification",
            "question": final_state["clarification_question"]
        })
    else:
        await websocket.send_json({
            "type": "final",
            "status": "completed",
            "report": final_state.get("final_report"),
            "source": final_state["finding"].source if final_state.get("finding") else None,
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