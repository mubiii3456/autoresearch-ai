import os
import json
from groq import Groq
from app.schemas.models import ResearchFinding, CriticFeedback
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


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

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        max_tokens=600,
        response_format={"type": "json_object"}
    )
    raw_text = response.choices[0].message.content
    data = json.loads(raw_text)
    return CriticFeedback(**data)