import os
import json
import uuid
from datetime import datetime
from mcp.server import MCPServer

mcp = MCPServer("document-storage-mcp")

STORAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
os.makedirs(STORAGE_DIR, exist_ok=True)


@mcp.tool()
def save_report(query: str, claim: str, source: str) -> dict:
    report_id = str(uuid.uuid4())[:8]

    report = {
        "id": report_id,
        "query": query,
        "claim": claim,
        "source": source,
        "created_at": datetime.now().isoformat()
    }

    file_path = os.path.join(STORAGE_DIR, f"{report_id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return {"report_id": report_id, "status": "saved"}


@mcp.tool()
def get_report(report_id: str) -> dict:
    file_path = os.path.join(STORAGE_DIR, f"{report_id}.json")

    if not os.path.exists(file_path):
        return {"error": f"Report '{report_id}' not found"}

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


@mcp.tool()
def list_reports() -> dict:
    reports = []

    for filename in os.listdir(STORAGE_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(STORAGE_DIR, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                reports.append({
                    "id": data["id"],
                    "query": data["query"],
                    "created_at": data["created_at"]
                })

    return {"reports": reports}


if __name__ == "__main__":
    mcp.run()