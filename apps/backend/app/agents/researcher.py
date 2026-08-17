import os
import json
from groq import Groq
from app.schemas.models import ResearchFinding
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def researcher_agent(query: str, rejected_claims: list[str] = None) -> ResearchFinding:
    system_prompt = """You are a Researcher Agent. Respond only in this exact JSON format, nothing else:
{"claim": "...", "source": "...", "confidence": 0.0}"""

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
    return ResearchFinding(**data)

