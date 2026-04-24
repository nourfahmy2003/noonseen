"""Purpose: fetch live general Walla Kelma targets from Datamuse."""

from backend.config import DATAMUSE_API_BASE
from backend.services.repeat_prevention import choose_records
from backend.utilities.debug import debug_log
from backend.utilities.http import fetch_json
from backend.utilities.ids import source_record_id


def _difficulty_query(category):
    if category in {"ولا كلمة عامة", "Walla Kelma English General"}:
        return {
            "easy": {"topics": "common objects", "max": 40, "sp": "*"},
            "medium": {"topics": "daily life", "max": 60, "sp": "*"},
            "hard": {"topics": "abstract concept", "max": 80, "sp": "*"},
        }
    return {
        "easy": {"topics": "general", "max": 40, "sp": "*"},
        "medium": {"topics": "general", "max": 60, "sp": "*"},
        "hard": {"topics": "general", "max": 80, "sp": "*"},
    }


def fetch_prompt(category, difficulty):
    query = _difficulty_query(category)[difficulty]
    debug_log("API REQUEST", "Calling API", {"url": DATAMUSE_API_BASE, "params": query})
    records = [
        item
        for item in fetch_json(DATAMUSE_API_BASE, query=query)
        if isinstance(item, dict) and str(item.get("word") or "").strip().isalpha()
    ]
    debug_log("API RESPONSE", "Raw response received", records[:3])
    picked = choose_records(
        f"walla:{category}:{difficulty}",
        records,
        1,
        lambda item: source_record_id("datamuse", category, item.get("word")),
    )[0]
    debug_log("WALLA", "Source record", picked)
    word = str(picked.get("word") or "").strip()
    debug_log("WALLA", "Secret generated", word)
    return {
        "id": source_record_id("datamuse", category, word),
        "difficulty": difficulty,
        "secret_value": word,
        "secret_value_ar": word,
        "display_hint_ar": "مثّل الكلمة بدون نطقها أو تهجئتها.",
        "metadata": {"score": picked.get("score")},
    }
