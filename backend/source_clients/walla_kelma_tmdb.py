"""Purpose: fetch live movie and series titles for Walla Kelma from TMDB."""

from backend.config import TMDB_API_BASE, TMDB_BEARER_TOKEN
from backend.services.repeat_prevention import choose_records
from backend.utilities.debug import debug_log
from backend.utilities.http import fetch_json
from backend.utilities.ids import source_record_id


def _endpoint_for_category(category):
    if category == "Walla Kelma English Series":
        return "/discover/tv", "TV مسلسل أو برنامج أجنبي"
    return "/discover/movie", "فيلم أو عمل أجنبي معروف"


def fetch_prompt(category, difficulty):
    if not TMDB_BEARER_TOKEN:
        debug_log("API ERROR", "Request failed", "TMDB bearer token is not configured.")
        raise ValueError("TMDB bearer token is not configured.")

    path, hint = _endpoint_for_category(category)
    page = 1 if difficulty == "easy" else 2 if difficulty == "medium" else 4
    debug_log(
        "API REQUEST",
        "Calling API",
        {"url": f"{TMDB_API_BASE}{path}", "params": {"language": "en-US", "sort_by": "popularity.desc", "page": page}},
    )
    records = fetch_json(
        f"{TMDB_API_BASE}{path}",
        headers={"Authorization": f"Bearer {TMDB_BEARER_TOKEN}"},
        query={
            "language": "en-US",
            "sort_by": "popularity.desc",
            "page": page,
        },
    ).get("results") or []
    debug_log("API RESPONSE", "Raw response received", records[:3] if isinstance(records, list) else records)
    records = [
        item
        for item in records
        if isinstance(item, dict) and str(item.get("title") or item.get("name") or "").strip()
    ]
    picked = choose_records(
        f"walla:{category}:{difficulty}",
        records,
        1,
        lambda item: source_record_id("tmdb", path, item.get("id")),
    )[0]
    debug_log("WALLA", "Source record", picked)
    secret = str(picked.get("title") or picked.get("name") or "").strip()
    debug_log("WALLA", "Secret generated", secret)
    return {
        "id": source_record_id("tmdb", path, picked.get("id")),
        "difficulty": difficulty,
        "secret_value": secret,
        "secret_value_ar": secret,
        "display_hint_ar": hint,
        "metadata": {"tmdb_id": picked.get("id"), "media_type": "tv" if "name" in picked else "movie"},
    }
