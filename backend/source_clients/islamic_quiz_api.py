"""Purpose: build reveal-style Islamic questions from the live IslamicQuizAPI source only."""

from backend.difficulty.rules import iter_difficulty_slots
from backend.normalization.questions import build_internal_question
from backend.services.repeat_prevention import choose_records
from backend.source_clients.islamic_quiz_api_records import fetch_islamic_quiz_category_records
from backend.utilities.debug import debug_log, debug_preview


def fetch_questions(selection, source_definition, cache):
    """Prepare six validated reveal-mode questions for one IslamicQuizAPI category."""
    category_name = selection["backend_category"]
    records = fetch_islamic_quiz_category_records(category_name, cache)
    prepared = []
    used_ids = set()

    for difficulty, points in iter_difficulty_slots():
        eligible = [
            record
            for record in records
            if record["difficulty"] == difficulty and record["stable_id"] not in used_ids
        ]
        picked = choose_records(
            f"quiz:islamicquizapi:{category_name}:{difficulty}",
            eligible,
            1,
            lambda record: record["stable_id"],
        )
        record = picked[0]
        used_ids.add(record["stable_id"])
        debug_log(
            "VALIDATION",
            "Checking question",
            {"question": record["question_ar"], "answer": record["answer_ar"], "difficulty": difficulty},
        )
        prepared.append(
            build_internal_question(
                question_id=record["stable_id"],
                category=category_name,
                difficulty=record["difficulty"],
                points=points,
                question_ar=record["question_ar"],
                answer_ar=record["answer_ar"],
                source=source_definition["source"],
                source_type=source_definition["source_type"],
                metadata={
                    "display_mode": "reveal_answer",
                    "source_record_id": record["stable_id"],
                    "source_question_id": record["source_question_id"],
                    "source_link": record["source_link"],
                    "source_level": record["source_level"],
                    "topic_slug": record["topic_slug"],
                    "topic_name_ar": record["topic_name_ar"],
                    "topic_description": record["topic_description"],
                    "category_id": record["category_id"],
                    "category_name_en": record["category_name_en"],
                    "source_section": record["source_section"],
                },
            )
        )

    debug_log("FINAL", "Questions ready", debug_preview(prepared, limit=5))
    return prepared
