"""Purpose: read the in-process IslamicQuizAPI provider for runtime play."""

from backend.data.islamic_quiz_api import (
    fetch_islamic_quiz_categories as fetch_internal_categories,
    fetch_islamic_quiz_topic_questions as fetch_internal_topic_questions,
    fetch_islamic_quiz_topics as fetch_internal_topics,
)
from backend.models.schemas import IslamicQuizApiCategory, IslamicQuizApiQuestionRecord, IslamicQuizApiTopic
from backend.utilities.debug import debug_log, debug_preview


ISLAMIC_QUIZ_REQUIRED_CATEGORIES = {
    "التفسير",
    "العقيدة",
    "الحديث",
    "الفقه",
    "التاريخ",
    "اللغة العربية",
}


def fetch_islamic_quiz_categories() -> list[IslamicQuizApiCategory]:
    """Return the in-process category list from the internal Islamic provider."""
    debug_log("API REQUEST", "Calling internal provider", {"provider": "islamic_quiz_api", "resource": "categories"})
    payload = fetch_internal_categories()
    debug_log("API RESPONSE", "Raw response received", debug_preview(payload, limit=3))
    if not isinstance(payload, list):
        raise ValueError("IslamicQuizAPI categories endpoint returned invalid payload")
    return payload


def fetch_islamic_quiz_topics(category_id: int) -> list[IslamicQuizApiTopic]:
    """Return all topics for one Islamic category id from the internal provider."""
    debug_log(
        "API REQUEST",
        "Calling internal provider",
        {"provider": "islamic_quiz_api", "resource": "topics", "category_id": category_id},
    )
    payload = fetch_internal_topics(category_id)
    debug_log("API RESPONSE", "Raw response received", debug_preview(payload, limit=3))
    if not isinstance(payload, list):
        raise ValueError(f"IslamicQuizAPI topics endpoint returned invalid payload for category {category_id}")
    return payload


def fetch_islamic_quiz_topic_questions(category_id: int, topic_slug: str) -> list[IslamicQuizApiQuestionRecord]:
    """Return all question records for one topic inside one Islamic category."""
    debug_log(
        "API REQUEST",
        "Calling internal provider",
        {
            "provider": "islamic_quiz_api",
            "resource": "questions",
            "category_id": category_id,
            "topic_slug": topic_slug,
        },
    )
    payload = fetch_internal_topic_questions(category_id, topic_slug)
    debug_log("API RESPONSE", "Raw response received", debug_preview(payload, limit=3))
    if not isinstance(payload, list):
        raise ValueError(
            f"IslamicQuizAPI topic questions endpoint returned invalid payload for category {category_id} topic {topic_slug}"
        )
    return payload


def is_islamic_quiz_api_available(required_categories=None):
    """Probe the live category list and ensure the required Arabic categories exist."""
    required = set(required_categories or ISLAMIC_QUIZ_REQUIRED_CATEGORIES)
    try:
        categories = fetch_islamic_quiz_categories()
    except Exception as error:
        debug_log("API ERROR", "Request failed", f"IslamicQuizAPI availability probe failed: {error}")
        return False

    available_names = {
        str(category.get("arabicName") or "").strip()
        for category in categories
        if isinstance(category, dict)
    }
    is_available = required.issubset(available_names)
    debug_log(
        "SOURCE",
        "IslamicQuizAPI live availability",
        {"available": is_available, "required": sorted(required), "available_names": sorted(available_names)},
    )
    return is_available
