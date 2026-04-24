"""Purpose: fetch live Open Trivia payloads without reading local cache files at runtime."""

import time

from backend.config import OPEN_TRIVIA_API_BASE
from backend.utilities.debug import debug_log
from backend.utilities.http import fetch_json


OPEN_TRIVIA_RESPONSE_CACHE = {}
OPEN_TRIVIA_CACHE_TTL_SECONDS = 90
OPEN_TRIVIA_RETRY_BACKOFF_SECONDS = (0.75, 1.5, 3.0)


def _get_cache_key(category_id, amount, difficulty, session_token, question_type, cache_bust):
    return (
        str(category_id),
        int(amount),
        str(difficulty or ""),
        str(session_token or ""),
        str(question_type or ""),
        str(cache_bust or ""),
    )


def _get_cached_payload(cache_key):
    cached = OPEN_TRIVIA_RESPONSE_CACHE.get(cache_key)
    now = time.time()
    if not cached:
        return None
    if cached["expires_at"] <= now:
        OPEN_TRIVIA_RESPONSE_CACHE.pop(cache_key, None)
        return None
    debug_log("API REQUEST", "Open Trivia cache hit", {"cache_key": cache_key, "expires_at": cached["expires_at"]})
    return cached["payload"]


def fetch_open_trivia_payload(
    category_id,
    *,
    amount,
    difficulty=None,
    session_token=None,
    question_type="multiple",
    cache_bust=None,
):
    """Purpose: pull Open Trivia rows; default type=multiple avoids boolean stems that are not reveal-friendly.
    
    Open Trivia DB is used for:
    - تاريخ (category_id=23)
    - تكنولوجيا (category_id=18)
    - عالم الحيوان (category_id=27)
    
    Always uses URL encoding and multiple-choice type for better reveal compatibility.
    """
    cache_key = _get_cache_key(category_id, amount, difficulty, session_token, question_type, cache_bust)
    cached_payload = _get_cached_payload(cache_key)
    if cached_payload is not None:
        return cached_payload

    query = {"category": category_id, "encode": "url3986", "amount": amount, "type": question_type}
    if difficulty:
        query["difficulty"] = difficulty
    if session_token:
        query["token"] = session_token
    
    # Map category IDs to backend category names for logging clarity.
    category_name_map = {
        "23": "تاريخ",
        "18": "تكنولوجيا",
        "27": "عالم الحيوان",
    }
    category_display = category_name_map.get(str(category_id), str(category_id))
    
    debug_log(
        "API REQUEST",
        f"Open Trivia API request for {category_display}",
        {
            "url": OPEN_TRIVIA_API_BASE,
            "category_id": category_id,
            "backend_category": category_display,
            "amount": amount,
            "difficulty": difficulty or "mixed",
            "type": question_type,
            "cache_bust": cache_bust,
        },
    )
    payload = fetch_json(
        OPEN_TRIVIA_API_BASE,
        query=query,
        max_attempts=1 + len(OPEN_TRIVIA_RETRY_BACKOFF_SECONDS),
        retry_backoff_seconds=OPEN_TRIVIA_RETRY_BACKOFF_SECONDS,
        retry_on_statuses={429},
    )
    
    debug_log(
        "API RESPONSE",
        f"Open Trivia response for {category_display}",
        {
            "response_code": payload.get("response_code"),
            "result_count": len(payload.get("results", [])) if isinstance(payload, dict) else 0,
        },
    )
    
    OPEN_TRIVIA_RESPONSE_CACHE[cache_key] = {
        "payload": payload,
        "expires_at": time.time() + OPEN_TRIVIA_CACHE_TTL_SECONDS,
    }
    return payload
