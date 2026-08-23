import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

app = FastAPI()
tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))


class SearchRequest(BaseModel):
    query: str


@app.post("/search")
def web_search(request: SearchRequest):
    response = tavily_client.search(query=request.query, max_results=3)

    results = []
    for item in response.get("results", []):
        results.append({
            "title": item.get("title"),
            "content": item.get("content"),
            "url": item.get("url")
        })

    return {"results": results}


@app.get("/health")
def health():
    return {"status": "ok"}