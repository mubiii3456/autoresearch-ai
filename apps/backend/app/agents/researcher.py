import json
from app.schemas.models import ResearchFinding
from app.mcp_clients.web_search_client import web_search
from app.security.prompt_guard import sanitize_search_results
from app.mcp_clients.finance_client import get_stock_quote
from app.agents.llm_helper import call_llm


def researcher_agent(query: str, rejected_claims: list[str] = None) -> dict:
    system_prompt = """You are a Researcher Agent with access to live web search results.

Only ask for clarification if the query is genuinely impossible to answer without more information (e.g. missing a company name, missing a specific year when it matters, or referring to something with no clear subject).

For general queries (like "latest news about X" or broad topics), use the search results provided to give the best possible answer instead of asking for clarification.

If clarification is needed, respond with:
{"needs_clarification": true, "question": "your clarification question"}

Otherwise respond only in this exact JSON format:
{"needs_clarification": false, "claim": "...", "source": "...", "confidence": 0.0}"""

    search_results = web_search(query)
    context = "\n".join([f"- {r['title']}: {r['content']}" for r in sanitize_search_results(search_results.get("results", []))])

    common_symbols = {"apple": "AAPL", "tesla": "TSLA", "microsoft": "MSFT", "google": "GOOGL", "amazon": "AMZN"}
    query_lower = query.lower()
    matched_symbol = next((sym for name, sym in common_symbols.items() if name in query_lower), None)

    if matched_symbol and ("stock" in query_lower or "price" in query_lower or "share" in query_lower):
        stock_data = get_stock_quote(matched_symbol)
        if "error" not in stock_data:
            context += f"\n\nLive stock data for {matched_symbol}: Price: {stock_data.get('price')}, Change: {stock_data.get('change')} ({stock_data.get('change_percent')})"
    safe_results = sanitize_search_results(search_results.get("results", []))
    context = "\n".join([f"- {r['title']}: {r['content']}" for r in safe_results])
    user_message = f"""Query: {query}

Search results:
{context}

Based on the above search results, provide your answer."""

    if rejected_claims:
        rejected_list = "\n".join(f"- {c}" for c in rejected_claims)
        user_message += f"""

The following claims were previously rejected. Do not repeat them, provide a different or more accurate claim:
{rejected_list}"""

    raw_text = call_llm(system_prompt, user_message, max_tokens=800)
    data = json.loads(raw_text)

    if data.get("needs_clarification"):
        return {"needs_clarification": True, "question": data["question"]}

    return {"needs_clarification": False, "finding": ResearchFinding(claim=data["claim"], source=data["source"], confidence=data["confidence"])}