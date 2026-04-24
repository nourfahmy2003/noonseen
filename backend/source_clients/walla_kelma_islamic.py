"""Purpose: fetch live Islamic acting targets for Walla Kelma from IslamicQuizAPI only."""

from backend.services.repeat_prevention import choose_records
from backend.source_clients.islamic_quiz_api_records import fetch_islamic_quiz_category_records
from backend.utilities.debug import debug_log
from backend.utilities.ids import source_record_id


WALLA_ISLAMIC_CATEGORIES = (
    "التفسير",
    "العقيدة",
    "الحديث",
    "الفقه",
    "التاريخ",
    "اللغة العربية",
)


def fetch_prompt(category, difficulty):
    records = []
    cache = {}
    for islamic_category in WALLA_ISLAMIC_CATEGORIES:
        records.extend(fetch_islamic_quiz_category_records(islamic_category, cache))
    picked = choose_records(
        f"walla:{category}:{difficulty}",
        [record for record in records if record["difficulty"] == difficulty],
        1,
        lambda item: item["stable_id"],
    )[0]
    debug_log("WALLA", "Source record", picked)
    secret = picked["answer_ar"]
    debug_log("WALLA", "Secret generated", secret)
    return {
        "id": source_record_id("islamicquizapi", picked["stable_id"]),
        "difficulty": difficulty,
        "secret_value": secret,
        "secret_value_ar": secret,
        "display_hint_ar": "مثّل معنى أو اسمًا إسلاميًا دون قول الجواب نفسه.",
        "metadata": {
            "source_question": picked["question_ar"],
            "source_link": picked["source_link"],
            "topic_name_ar": picked["topic_name_ar"],
            "category_name_ar": picked["category_name_ar"],
        },
    }
