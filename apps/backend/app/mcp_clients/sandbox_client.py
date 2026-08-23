import os
import requests

SANDBOX_MCP_URL = os.environ.get("SANDBOX_MCP_URL", "http://localhost:8004")


def calculate(expression: str) -> dict:
    response = requests.post(f"{SANDBOX_MCP_URL}/calculate", json={"expression": expression}, timeout=15)
    return response.json()