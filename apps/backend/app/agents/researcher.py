import os
import json
from groq import Groq
from app.schemas.models import ResearchFinding
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def researcher_agent(query: str, rejected_claims: list[str] = None) -> ResearchFinding:
    system_prompt = """You are a Researcher Agent. If the query is ambiguous or unclear, respond with:
{"needs_clarification": true, "question": "your clarification question"}

Otherwise respond only in this exact JSON format:
{"needs_clarification": false, "claim": "...", "source": "...", "confidence": 0.0}"""
    user_message = query

    if rejected_claims:
        rejected_list = "\n".join(f"- {c}" for c in rejected_claims)
        user_message = f"""{query}

The following claims were previously rejected. Do not repeat them, provide a different or more accurate claim:
{rejected_list}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        max_tokens=300
    )

    raw_text = response.choices[0].message.content
    data = json.loads(raw_text)
    if data.get("needs_clarification"):
        return {"needs_clarification": True, "question": data["question"]}

    return {"needs_clarification": False, "finding": ResearchFinding(claim=data["claim"], source=data["source"], confidence=data["confidence"])}
    

