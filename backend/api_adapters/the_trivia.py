"""Purpose: fetch live The Trivia API payloads without paid Arabic query params."""

import time

from backend.config import THE_TRIVIA_API_BASE, THE_TRIVIA_API_KEY
from backend.utilities.debug import debug_log
from backend.utilities.http import fetch_json


THE_TRIVIA_RESPONSE_CACHE = {}
THE_TRIVIA_CACHE_TTL_SECONDS = 120
THE_TRIVIA_RETRY_BACKOFF_SECONDS = (0.5, 1.0)


def _get_cache_key(categories, difficulty, limit):
    return (tuple(categories), str(difficulty or ""), int(limit))


def _get_cached_payload(cache_key):
    cached = THE_TRIVIA_RESPONSE_CACHE.get(cache_key)
    now = time.time()
    if not cached:
        return None
    if cached["expires_at"] <= now:
        THE_TRIVIA_RESPONSE_CACHE.pop(cache_key, None)
        return None
    debug_log("API REQUEST", "The Trivia cache hit", {"cache_key": cache_key, "expires_at": cached["expires_at"]})
    return cached["payload"]


def fetch_the_trivia_payload(*, categories, difficulty=None, limit=18):
    cache_key = _get_cache_key(categories, difficulty, limit)
    cached_payload = _get_cached_payload(cache_key)
    if cached_payload is not None:
        return cached_payload

    query = {"limit": limit, "categories": ",".join(categories)}
    if difficulty:
        query["difficulties"] = difficulty
    headers = {"x-api-key": THE_TRIVIA_API_KEY} if THE_TRIVIA_API_KEY else None
    
    # Build the full URL for logging (never print raw API keys).
    url_params = f"?limit={limit}&categories={query['categories']}"
    if difficulty:
        url_params += f"&difficulties={difficulty}"
    full_url_preview = f"{THE_TRIVIA_API_BASE}{url_params}"
    
    debug_log(
        "API REQUEST",
        "The Trivia API v2 questions request",
        {
            "url": full_url_preview,
            "categories_csv": query.get("categories"),
            "limit": query.get("limit"),
            "difficulties": query.get("difficulties"),
            "has_api_key_header": bool(THE_TRIVIA_API_KEY),
        },
    )
    payload = fetch_json(
        THE_TRIVIA_API_BASE,
        headers=headers,
        query=query,
        max_attempts=1 + len(THE_TRIVIA_RETRY_BACKOFF_SECONDS),
        retry_backoff_seconds=THE_TRIVIA_RETRY_BACKOFF_SECONDS,
        retry_on_statuses={429},
    )
    THE_TRIVIA_RESPONSE_CACHE[cache_key] = {
        "payload": payload,
        "expires_at": time.time() + THE_TRIVIA_CACHE_TTL_SECONDS,
    }
    return payload
