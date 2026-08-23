import os
import requests

STORAGE_MCP_URL = os.environ.get("STORAGE_MCP_URL", "http://localhost:8003")


def save_report(query: str, claim: str, source: str, tokens: int = 0, cost: float = 0.0) -> dict:
    response = requests.post(f"{STORAGE_MCP_URL}/reports", json={
        "query": query, "claim": claim, "source": source, "tokens": tokens, "cost": cost
    }, timeout=15)
    return response.json()


def get_report(report_id: str) -> dict:
    response = requests.get(f"{STORAGE_MCP_URL}/reports/{report_id}", timeout=15)
    return response.json()


def list_reports() -> dict:
    response = requests.get(f"{STORAGE_MCP_URL}/reports", timeout=15)
    return response.json()