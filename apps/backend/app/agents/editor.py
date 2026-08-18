import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def editor_agent(draft_report: str, source: str) -> str:
    system_prompt = """You are an Editor Agent. Polish the given draft report for clarity, grammar, and professional tone. Keep the meaning exactly the same, just improve the writing quality. Add a citation line at the end referencing the source.

Respond only in this exact JSON format:
{"final_report": "your polished report here"}"""

    user_message = f"""Draft report: {draft_report}
Source to cite: {source}"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        max_tokens=500,
        response_format={"type": "json_object"}
    )

    data = json.loads(response.choices[0].message.content)
    return data["final_report"]