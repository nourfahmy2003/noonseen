"""Purpose: fetch live API Ninjas logo records with centralized auth handling.

Each request must include either `name` or `ticker` (never both empty). Responses are capped
at 10 rows, so the caller fans out multiple curated seeds in `logo_brand_seeds.py`.
"""

import time

from backend.config import API_NINJAS_API_KEY, API_NINJAS_LOGO_API_BASE
from backend.utilities.debug import debug_log
from backend.utilities.http import fetch_json


API_NINJAS_LOGO_CACHE = {}
API_NINJAS_LOGO_CACHE_TTL_SECONDS = 300


def _cache_key(name=None, ticker=None):
    return (str(name or "").strip().lower(), str(ticker or "").strip().upper())


def _get_cached_payload(cache_key):
    cached = API_NINJAS_LOGO_CACHE.get(cache_key)
    now = time.time()
    if not cached:
        return None
    if cached["expires_at"] <= now:
        API_NINJAS_LOGO_CACHE.pop(cache_key, None)
        return None
    debug_log("API REQUEST", "API Ninjas logo cache hit", {"cache_key": cache_key})
    return cached["payload"]


def fetch_api_ninjas_logo_payload(*, name=None, ticker=None):
    query_name = str(name or "").strip()
    query_ticker = str(ticker or "").strip().upper()
    if not query_name and not query_ticker:
        raise ValueError("API Ninjas logo requests require either a name or ticker query")

    cache_key = _cache_key(name=query_name, ticker=query_ticker)
    cached_payload = _get_cached_payload(cache_key)
    if cached_payload is not None:
        return cached_payload

    query = {"name": query_name} if query_name else {"ticker": query_ticker}
    debug_log(
        "API REQUEST",
        "Preparing API Ninjas Logo adapter request",
        {
            "url": API_NINJAS_LOGO_API_BASE,
            "params": query,
            "has_api_ninjas_key": bool(API_NINJAS_API_KEY),
        },
    )
    payload = fetch_json(
        API_NINJAS_LOGO_API_BASE,
        headers={"x-api-key": API_NINJAS_API_KEY},
        query=query,
        max_attempts=2,
        retry_backoff_seconds=(1.0,),
        retry_on_statuses={429},
    )
    API_NINJAS_LOGO_CACHE[cache_key] = {
        "payload": payload,
        "expires_at": time.time() + API_NINJAS_LOGO_CACHE_TTL_SECONDS,
    }
    return payload
