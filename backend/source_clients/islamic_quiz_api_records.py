"""Purpose: normalize IslamicQuizAPI category and topic records into validated Arabic source records."""

from backend.api_adapters.islamic_quiz_api import (
    fetch_islamic_quiz_categories,
    fetch_islamic_quiz_topic_questions,
    fetch_islamic_quiz_topics,
)
from backend.arabic.transform import is_valid_arabic_output, normalize_arabic_text
from backend.difficulty.rules import normalize_islamic_quiz_difficulty
from backend.utilities.debug import debug_log, debug_preview
from backend.utilities.ids import source_record_id, stable_hash


def _find_category(categories, category_name):
    for category in categories:
        if not isinstance(category, dict):
            continue
        if normalize_arabic_text(category.get("arabicName")) == normalize_arabic_text(category_name):
            return category
    raise ValueError(f"IslamicQuizAPI category not found: {category_name}")


def _extract_correct_answer(record):
    answers = record.get("answers") if isinstance(record, dict) else None
    if not isinstance(answers, list):
        return ""
    for answer in answers:
        if isinstance(answer, dict) and int(answer.get("t") or 0) == 1:
            return normalize_arabic_text(answer.get("answer"))
    return ""


def _normalize_source_record(category, topic, raw_record):
    debug_log("RAW RECORD", "Incoming data", raw_record)
    question_ar = normalize_arabic_text(raw_record.get("q"))
    answer_ar = _extract_correct_answer(raw_record)
    category_name_ar = normalize_arabic_text(category.get("arabicName"))
    topic_name_ar = normalize_arabic_text(topic.get("name"))
    difficulty = normalize_islamic_quiz_difficulty(raw_record.get("level"), question_ar, answer_ar)

    if not question_ar:
        debug_log("REJECTED", "Reason", "missing question")
        return None
    if not answer_ar:
        debug_log("REJECTED", "Reason", "missing answer")
        return None
    if not category_name_ar:
        debug_log("REJECTED", "Reason", "missing category")
        return None
    if difficulty not in {"easy", "medium", "hard"}:
        debug_log("REJECTED", "Reason", "missing difficulty")
        return None
    if not is_valid_arabic_output(question_ar):
        debug_log("REJECTED", "Reason", "invalid Arabic question")
        return None
    if not is_valid_arabic_output(answer_ar, allow_digits=True):
        debug_log("REJECTED", "Reason", "invalid Arabic answer")
        return None

    stable_id = source_record_id(
        "islamicquizapi",
        category.get("id"),
        topic.get("slug"),
        raw_record.get("id") or stable_hash(question_ar, answer_ar),
    )
    normalized = {
        "stable_id": stable_id,
        "source_question_id": raw_record.get("id"),
        "category_id": category.get("id"),
        "category_name_ar": category_name_ar,
        "category_name_en": category.get("englishName"),
        "topic_slug": topic.get("slug"),
        "topic_name_ar": topic_name_ar,
        "topic_description": topic.get("description"),
        "question_ar": question_ar,
        "answer_ar": answer_ar,
        "difficulty": difficulty,
        "source_level": raw_record.get("level"),
        "source_link": raw_record.get("link"),
        "source_section": raw_record.get("section"),
    }
    debug_log("TRANSFORM", "Built question", debug_preview(normalized, limit=8))
    return normalized


def fetch_islamic_quiz_category_records(category_name, cache):
    """Fetch one Islamic category and flatten its topic questions into normalized records."""
    categories_cache_key = "islamic_quiz_api_categories"
    if categories_cache_key not in cache:
        cache[categories_cache_key] = fetch_islamic_quiz_categories()

    category = _find_category(cache[categories_cache_key], category_name)
    topics_cache_key = f"islamic_quiz_api_topics:{category['id']}"
    if topics_cache_key not in cache:
        cache[topics_cache_key] = fetch_islamic_quiz_topics(category["id"])
    debug_log(
        "FINAL",
        "IslamicQuizAPI source response size",
        {"category": category_name, "topic_count": len(cache[topics_cache_key])},
    )

    records = []
    for topic in cache[topics_cache_key]:
        topic_slug = str(topic.get("slug") or "").strip()
        if not topic_slug:
            debug_log("REJECTED", "Reason", "missing topic slug")
            continue
        questions_cache_key = f"islamic_quiz_api_questions:{category['id']}:{topic_slug}"
        if questions_cache_key not in cache:
            cache[questions_cache_key] = fetch_islamic_quiz_topic_questions(category["id"], topic_slug)
        debug_log(
            "FINAL",
            "IslamicQuizAPI topic response size",
            {
                "category": category_name,
                "topic_slug": topic_slug,
                "record_count": len(cache[questions_cache_key]),
            },
        )

        for raw_record in cache[questions_cache_key]:
            normalized = _normalize_source_record(category, topic, raw_record)
            if normalized:
                records.append(normalized)

    debug_log(
        "FINAL",
        f'IslamicQuizAPI normalized records ready for "{category_name}"',
        {"count": len(records), "preview": debug_preview(records, limit=5)},
    )
    return records
