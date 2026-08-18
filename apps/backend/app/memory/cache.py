import redis
import json
import hashlib

client = redis.Redis(host="localhost", port=6379, decode_responses=True)

CACHE_TTL_SECONDS = 3600


def _make_cache_key(query: str) -> str:
    return f"research_cache:{hashlib.md5(query.lower().strip().encode()).hexdigest()}"


def get_cached_result(query: str):
    key = _make_cache_key(query)
    cached = client.get(key)
    if cached:
        return json.loads(cached)
    return None


def set_cached_result(query: str, claim: str, source: str, confidence: float):
    key = _make_cache_key(query)
    value = json.dumps({"claim": claim, "source": source, "confidence": confidence})
    client.setex(key, CACHE_TTL_SECONDS, value)