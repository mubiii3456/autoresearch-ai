import os
import requests

WEB_SEARCH_URL = os.environ.get("WEB_SEARCH_MCP_URL", "http://localhost:8001")


def web_search(query: str) -> dict:
    response = requests.post(f"{WEB_SEARCH_URL}/search", json={"query": query}, timeout=15)
    return response.json()