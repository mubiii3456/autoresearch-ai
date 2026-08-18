import os
import requests
from dotenv import load_dotenv
from mcp.server import MCPServer

load_dotenv()

mcp = MCPServer("finance-news-mcp")
API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"


@mcp.tool()
def get_stock_quote(symbol: str) -> dict:
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": API_KEY
    }

    response = requests.get(BASE_URL, params=params, timeout=10)
    data = response.json()

    quote = data.get("Global Quote", {})

    if not quote:
        return {"error": f"No data found for symbol '{symbol}'"}

    return {
        "symbol": quote.get("01. symbol"),
        "price": quote.get("05. price"),
        "change": quote.get("09. change"),
        "change_percent": quote.get("10. change percent"),
        "volume": quote.get("06. volume")
    }


@mcp.tool()
def get_company_overview(symbol: str) -> dict:
    params = {
        "function": "OVERVIEW",
        "symbol": symbol,
        "apikey": API_KEY
    }

    response = requests.get(BASE_URL, params=params, timeout=10)
    data = response.json()

    if not data or "Symbol" not in data:
        return {"error": f"No overview found for symbol '{symbol}'"}

    return {
        "name": data.get("Name"),
        "description": data.get("Description"),
        "sector": data.get("Sector"),
        "market_cap": data.get("MarketCapitalization"),
        "pe_ratio": data.get("PERatio"),
        "revenue_ttm": data.get("RevenueTTM")
    }


if __name__ == "__main__":
    mcp.run()