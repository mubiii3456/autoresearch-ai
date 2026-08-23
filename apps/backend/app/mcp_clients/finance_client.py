import os
import requests

FINANCE_MCP_URL = os.environ.get("FINANCE_MCP_URL", "http://localhost:8002")


def get_stock_quote(symbol: str) -> dict:
    response = requests.post(f"{FINANCE_MCP_URL}/quote", json={"symbol": symbol}, timeout=15)
    return response.json()


def get_company_overview(symbol: str) -> dict:
    response = requests.post(f"{FINANCE_MCP_URL}/overview", json={"symbol": symbol}, timeout=15)
    return response.json()