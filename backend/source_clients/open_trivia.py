"""Purpose: optional standalone Open Trivia client (board still prefers the_trivia router + LibreTranslate)."""

import html
from urllib.parse import unquote

from backend.api_adapters.open_trivia import fetch_open_trivia_payload
from backend.difficulty.rules import iter_difficulty_slots, normalize_difficulty
from backend.normalization.questions import build_internal_question
from backend.services.repeat_prevention import choose_records
from backend.services.translation_service import translate_quiz_pair
from backend.utilities.debug import debug_log, debug_preview
from backend.utilities.ids import source_record_id, stable_hash


OPEN_TRIVIA_CATEGORY_BY_UI_ID = {
    "general-technology": 18,
    "general-general-knowledge": 9,
    "general-history": 23,
    "general-animals": 27,
}


def _decode(value):
    return html.unescape(unquote(str(value or ""))).strip()


def _fetch_results(category_id):
    debug_log(
        "API REQUEST",
        "Fetching Open Trivia results for source client",
        {"category_id": category_id, "amount": 18},
    )
    payload = fetch_open_trivia_payload(category_id, amount=18, question_type="multiple")
    results = payload.get("results") if isinstance(payload, dict) else None
    debug_log("API RESPONSE", "Open Trivia payload received", debug_preview(results, limit=3))
    if payload.get("response_code") != 0 or not isinstance(results, list):
        debug_log("API ERROR", "Request failed", f"Open Trivia request failed for category {category_id}")
        raise ValueError(f"Open Trivia request failed for category {category_id}")
    return choose_records(
        f"quiz:opentdb:{category_id}",
        results,
        6,
        lambda question: source_record_id(
            "opentdb",
            category_id,
            stable_hash(question.get("question"), question.get("correct_answer")),
        ),
    )


def fetch_questions(selection, source_definition, _cache):
    category_id = OPEN_TRIVIA_CATEGORY_BY_UI_ID.get(selection["ui_subcategory_id"])
    if not category_id:
        debug_log("REJECTED", "Reason", f"No Open Trivia category configured for {selection['ui_subcategory_id']}")
        raise ValueError(f"No Open Trivia category is configured for {selection['ui_subcategory_id']}")

    prepared = []
    results = _fetch_results(category_id)
    for index, ((slot_difficulty, points), question) in enumerate(zip(iter_difficulty_slots(), results), start=1):
        debug_log("RAW RECORD", "Incoming data", question)
        answer = _decode(question.get("correct_answer") or "")
        question_en = _decode(question.get("question") or "")
        try:
            question_ar, answer_ar = translate_quiz_pair(question_en=question_en, answer_en=answer)
        except Exception as error:
            debug_log(
                "REJECTED",
                "Reason",
                {"reason": str(error), "question_en": question_en[:120], "answer": answer[:80]},
            )
            continue
        debug_log(
            "TRANSFORM",
            "Built question",
            {
                "question_ar": question_ar[:120],
                "answer_ar": answer_ar[:80],
                "difficulty": normalize_difficulty(question.get("difficulty"), slot_difficulty),
                "slot_index": index,
            },
        )
        record_id = source_record_id("opentdb", category_id, stable_hash(question_en, answer))
        prepared.append(
            build_internal_question(
                question_id=record_id,
                category=selection["backend_category"],
                difficulty=normalize_difficulty(question.get("difficulty"), slot_difficulty),
                points=points,
                question_ar=question_ar,
                answer_ar=answer_ar,
                source=source_definition["source"],
                source_type=source_definition["source_type"],
                metadata={
                    "source_record_id": record_id,
                    "slot_index": index,
                    "display_mode": "reveal_answer",
                    "source_question": question_en,
                    "source_answer": answer,
                },
                needs_review=False,
            )
        )

    if len(prepared) != 6:
        debug_log(
            "REJECTED",
            "Reason",
            f"Open Trivia returned insufficient validated Arabic results for {selection['backend_category']}",
        )
        raise ValueError(f"Open Trivia returned insufficient validated Arabic results for {selection['backend_category']}")
    debug_log("FINAL", "Questions ready", debug_preview(prepared, limit=5))
    return prepared
