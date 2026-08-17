import os
import json
from groq import Groq
from dotenv import load_dotenv
from app.schemas.models import ResearchFinding
from app.mcp_clients.web_search_client import web_search

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def researcher_agent(query: str, rejected_claims: list[str] = None) -> dict:
    system_prompt = """You are a Researcher Agent with access to live web search results.

Only ask for clarification if the query is genuinely impossible to answer without more information (e.g. missing a company name, missing a specific year when it matters, or referring to something with no clear subject).

For general queries (like "latest news about X" or broad topics), use the search results provided to give the best possible answer instead of asking for clarification.

If clarification is needed, respond with:
{"needs_clarification": true, "question": "your clarification question"}

Otherwise respond only in this exact JSON format:
{"needs_clarification": false, "claim": "...", "source": "...", "confidence": 0.0}"""

    search_results = web_search(query)
    context = "\n".join([f"- {r['title']}: {r['content']}" for r in search_results.get("results", [])])

    user_message = f"""Query: {query}

Search results:
{context}

Based on the above search results, provide your answer."""

    if rejected_claims:
        rejected_list = "\n".join(f"- {c}" for c in rejected_claims)
        user_message += f"""

The following claims were previously rejected. Do not repeat them, provide a different or more accurate claim:
{rejected_list}"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        max_tokens=800,
        response_format={"type": "json_object"}
    )

    raw_text = response.choices[0].message.content
    data = json.loads(raw_text)

    if data.get("needs_clarification"):
        return {"needs_clarification": True, "question": data["question"]}

    return {"needs_clarification": False, "finding": ResearchFinding(claim=data["claim"], source=data["source"], confidence=data["confidence"])}