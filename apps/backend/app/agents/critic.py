import json
from app.schemas.models import ResearchFinding, CriticFeedback
from app.agents.llm_helper import call_llm
from app.mcp_clients.sandbox_client import calculate


def critic_agent(finding: ResearchFinding) -> CriticFeedback:
    system_prompt = """You are a Critic Agent. The Researcher Agent has access to live, real-time web search results that may include information beyond your own training knowledge cutoff.

Do NOT reject a claim just because it references dates, events, or facts that seem to be "in the future" relative to your training data. The Researcher's information comes from live web search and should be treated as current and valid on that basis alone.

Only reject a claim if:
- It contradicts itself internally
- The confidence score seems unreasonably high for a vague or speculative statement
- No source is provided at all
- The claim is clearly a hallucination unrelated to the query

Respond only in this exact JSON format, nothing else:
{"approved": true, "reason": "..."}"""

    user_message = f"Claim: {finding.claim}\nSource: {finding.source}\nConfidence: {finding.confidence}"

    raw_text = call_llm(system_prompt, user_message, max_tokens=400)
    data = json.loads(raw_text)
    confidence_percent = calculate(f"{finding.confidence} * 100")
    print(f"Confidence (via Sandbox MCP calculation): {confidence_percent.get('result')}%")
    return CriticFeedback(**data)