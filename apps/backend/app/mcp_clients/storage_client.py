import asyncio
import os
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "..", ".."))

SERVER_PYTHON = os.path.join(PROJECT_ROOT, "mcp-servers", "document-storage-mcp", "venv", "Scripts", "python.exe")
SERVER_SCRIPT = os.path.join(PROJECT_ROOT, "mcp-servers", "document-storage-mcp", "server.py")

SERVER_PARAMS = StdioServerParameters(
    command=SERVER_PYTHON,
    args=[SERVER_SCRIPT]
)


async def _call_tool_async(tool_name: str, arguments: dict) -> dict:
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            raw_text = result.content[0].text
            return json.loads(raw_text)


def save_report(query: str, claim: str, source: str) -> dict:
    return asyncio.run(_call_tool_async("save_report", {"query": query, "claim": claim, "source": source}))


def get_report(report_id: str) -> dict:
    return asyncio.run(_call_tool_async("get_report", {"report_id": report_id}))


def list_reports() -> dict:
    return asyncio.run(_call_tool_async("list_reports", {}))