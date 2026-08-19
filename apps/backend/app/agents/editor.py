import json
from app.agents.llm_helper import call_llm


def editor_agent(draft_report: str, source: str) -> str:
    system_prompt = """You are an Editor Agent. Polish the given draft report for clarity, grammar, and professional tone. Keep the meaning exactly the same, just improve the writing quality. Add a citation line at the end referencing the source.

Respond only in this exact JSON format:
{"final_report": "your polished report here"}"""

    user_message = f"""Draft report: {draft_report}
Source to cite: {source}"""

    raw_text = call_llm(system_prompt, user_message, max_tokens=500)
    data = json.loads(raw_text)
    return data["final_report"]