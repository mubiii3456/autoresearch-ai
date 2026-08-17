import os
import json
from groq import Groq
from app.schemas.models import ResearchFinding, CriticFeedback
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def critic_agent(finding: ResearchFinding) -> CriticFeedback:
    system_prompt = """You are a Critic Agent. Check the claim, source, and confidence given to you.
Respond only in this exact JSON format, nothing else:
{"approved": true, "reason": "..."}"""

    user_message = f"Claim: {finding.claim}\nSource: {finding.source}\nConfidence: {finding.confidence}"

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        max_tokens=200
    )

    raw_text = response.choices[0].message.content
    data = json.loads(raw_text)
    return CriticFeedback(**data)