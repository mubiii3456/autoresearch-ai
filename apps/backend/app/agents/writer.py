import json
from app.agents.llm_helper import call_llm


def writer_agent(query: str, claim: str, source: str) -> str:
    system_prompt = """You are a Writer Agent. Given a verified research finding, write a clear, well-structured report paragraph (3-5 sentences) that directly answers the original query. Write in a professional, informative tone. Do not add information beyond what is given.

Respond only in this exact JSON format:
{"report": "your written report here"}"""

    user_message = f"""Original query: {query}
Verified claim: {claim}
Source: {source}"""

    raw_text = call_llm(system_prompt, user_message, max_tokens=500)
    data = json.loads(raw_text)
    return data["report"]