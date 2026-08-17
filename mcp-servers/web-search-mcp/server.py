import os
from dotenv import load_dotenv
from tavily import TavilyClient
from mcp.server import MCPServer

load_dotenv()

mcp = MCPServer("web-search-mcp")
tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))


@mcp.tool()
def web_search(query: str) -> dict:
    response = tavily_client.search(query=query, max_results=3)

    results = []
    for item in response.get("results", []):
        results.append({
            "title": item.get("title"),
            "content": item.get("content"),
            "url": item.get("url")
        })

    return {"results": results}


if __name__ == "__main__":
    mcp.run()