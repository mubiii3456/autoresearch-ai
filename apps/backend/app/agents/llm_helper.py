import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

PRIMARY_MODEL = "openai/gpt-oss-120b"
FALLBACK_MODEL = "qwen/qwen3.6-27b"
COST_PER_1K_TOKENS = 0.0002


def call_llm(system_prompt: str, user_message: str, max_tokens: int = 500) -> dict:
    models_to_try = [PRIMARY_MODEL, FALLBACK_MODEL]

    last_error = None
    response = None

    for model in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )
            break
        except Exception as e:
            print(f"Model {model} failed ({e}).")
            last_error = e
            continue

    if response is None:
        raise last_error

    total_tokens = response.usage.total_tokens
    cost = (total_tokens / 1000) * COST_PER_1K_TOKENS

    return {
        "content": response.choices[0].message.content,
        "tokens": total_tokens,
        "cost": cost
    }