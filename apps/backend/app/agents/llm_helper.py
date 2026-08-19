import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

PRIMARY_MODEL = "openai/gpt-oss-120b"
FALLBACK_MODEL = "openai/gpt-oss-20b"

COST_PER_1K_TOKENS = 0.0002


def call_llm(system_prompt: str, user_message: str, max_tokens: int = 500) -> dict:
    try:
        response = client.chat.completions.create(
            model=PRIMARY_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
    except Exception as e:
        print(f"Primary model failed ({e}). Retrying with fallback model...")
        response = client.chat.completions.create(
            model=FALLBACK_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )

    total_tokens = response.usage.total_tokens
    cost = (total_tokens / 1000) * COST_PER_1K_TOKENS

    return {
        "content": response.choices[0].message.content,
        "tokens": total_tokens,
        "cost": cost
    }