import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"


class SymbolRequest(BaseModel):
    symbol: str


@app.post("/quote")
def get_stock_quote(request: SymbolRequest):
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": request.symbol,
        "apikey": API_KEY
    }

    response = requests.get(BASE_URL, params=params, timeout=10)
    data = response.json()

    quote = data.get("Global Quote", {})

    if not quote:
        return {"error": f"No data found for symbol '{request.symbol}'"}

    return {
        "symbol": quote.get("01. symbol"),
        "price": quote.get("05. price"),
        "change": quote.get("09. change"),
        "change_percent": quote.get("10. change percent"),
        "volume": quote.get("06. volume")
    }


@app.post("/overview")
def get_company_overview(request: SymbolRequest):
    params = {
        "function": "OVERVIEW",
        "symbol": request.symbol,
        "apikey": API_KEY
    }

    response = requests.get(BASE_URL, params=params, timeout=10)
    data = response.json()

    if not data or "Symbol" not in data:
        return {"error": f"No overview found for symbol '{request.symbol}'"}

    return {
        "name": data.get("Name"),
        "description": data.get("Description"),
        "sector": data.get("Sector"),
        "market_cap": data.get("MarketCapitalization"),
        "pe_ratio": data.get("PERatio"),
        "revenue_ttm": data.get("RevenueTTM")
    }


@app.get("/health")
def health():
    return {"status": "ok"}