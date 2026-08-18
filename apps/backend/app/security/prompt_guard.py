import re

SUSPICIOUS_PATTERNS = [
    r"ignore (all )?(previous|above) instructions",
    r"disregard (all )?(previous|above) instructions",
    r"you are now",
    r"new instructions?:",
    r"system prompt",
    r"act as",
    r"forget everything",
]


def sanitize_search_results(results: list[dict]) -> list[dict]:
    cleaned = []

    for item in results:
        content = item.get("content", "")
        title = item.get("title", "")

        is_suspicious = False
        for pattern in SUSPICIOUS_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE) or re.search(pattern, title, re.IGNORECASE):
                is_suspicious = True
                break

        if not is_suspicious:
            cleaned.append(item)

    return cleaned