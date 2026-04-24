"""Purpose: fetch live football acting targets for Walla Kelma from API-Football."""

from backend.config import API_FOOTBALL_API_BASE, API_FOOTBALL_API_KEY
from backend.services.repeat_prevention import choose_records
from backend.utilities.debug import debug_log
from backend.utilities.http import fetch_json
from backend.utilities.ids import source_record_id


def fetch_prompt(category, difficulty):
    if not API_FOOTBALL_API_KEY:
        debug_log("API ERROR", "Request failed", "API-Football key is not configured.")
        raise ValueError("API-Football key is not configured.")

    endpoint = "/players/topscorers" if difficulty == "hard" else "/teams"
    query = {"league": 39, "season": 2023} if endpoint.endswith("topscorers") else {"league": 39, "season": 2023}
    debug_log("API REQUEST", "Calling API", {"url": f"{API_FOOTBALL_API_BASE}{endpoint}", "params": query})
    payload = fetch_json(
        f"{API_FOOTBALL_API_BASE}{endpoint}",
        headers={"x-apisports-key": API_FOOTBALL_API_KEY},
        query=query,
    )
    responses = payload.get("response") if isinstance(payload, dict) else None
    debug_log("API RESPONSE", "Raw response received", responses[:3] if isinstance(responses, list) else responses)
    if not isinstance(responses, list) or not responses:
        debug_log("REJECTED", "Reason", "API-Football returned no usable records.")
        raise ValueError("API-Football returned no usable records.")

    picked = choose_records(
        f"walla:{category}:{difficulty}",
        responses,
        1,
        lambda item: source_record_id("apifootball", endpoint, (item.get("team") or item.get("player") or {}).get("id")),
    )[0]
    debug_log("WALLA", "Source record", picked)
    entity = picked.get("player") or picked.get("team") or {}
    secret = str(entity.get("name") or "").strip()
    debug_log("WALLA", "Secret generated", secret)
    return {
        "id": source_record_id("apifootball", endpoint, entity.get("id")),
        "difficulty": difficulty,
        "secret_value": secret,
        "secret_value_ar": secret,
        "display_hint_ar": "مثّل الاسم الكروي دون ذكر الحروف أو النادي مباشرة.",
        "metadata": {"entity_type": "player" if "player" in picked else "team"},
    }
