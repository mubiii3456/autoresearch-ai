import asyncio
import os
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "..", ".."))

SERVER_PYTHON = os.path.join(PROJECT_ROOT, "mcp-servers", "web-search-mcp", "venv", "Scripts", "python.exe")
SERVER_SCRIPT = os.path.join(PROJECT_ROOT, "mcp-servers", "web-search-mcp", "server.py")

SERVER_PARAMS = StdioServerParameters(
    command=SERVER_PYTHON,
    args=[SERVER_SCRIPT]
)


async def _search_async(query: str) -> dict:
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("web_search", {"query": query})
            raw_text = result.content[0].text
            return json.loads(raw_text)


def web_search(query: str) -> dict:
    return asyncio.run(_search_async(query))