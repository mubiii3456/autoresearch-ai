import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def writer_agent(query: str, claim: str, source: str) -> str:
    system_prompt = """You are a Writer Agent. Given a verified research finding, write a clear, well-structured report paragraph (3-5 sentences) that directly answers the original query. Write in a professional, informative tone. Do not add information beyond what is given.

Respond only in this exact JSON format:
{"report": "your written report here"}"""

    user_message = f"""Original query: {query}
Verified claim: {claim}
Source: {source}"""

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
    return data["report"]