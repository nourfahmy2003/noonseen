"""Purpose: validate and build reveal-mode internal questions from live sources only (no MCQ payloads)."""

from backend.arabic.transform import is_valid_arabic_output
from backend.models.schemas import InternalQuestion
from backend.utilities.debug import debug_log


VALID_DIFFICULTIES = {"easy", "medium", "hard"}


def _normalize_metadata(metadata):
    normalized = dict(metadata or {})
    display_mode = str(normalized.get("display_mode") or "").strip()
    if display_mode not in {"reveal_answer", "reveal_visual"}:
        display_mode = "reveal_visual" if normalized.get("visual") else "reveal_answer"
    normalized["display_mode"] = display_mode
    return normalized


def validate_internal_question(question: InternalQuestion) -> InternalQuestion:
    debug_log(
        "VALIDATION",
        "Checking question",
        {
            "question": question.get("question_ar"),
            "answer": question.get("answer_ar"),
            "difficulty": question.get("difficulty"),
            "id": question.get("id"),
        },
    )
    required_fields = (
        "id",
        "category",
        "difficulty",
        "points",
        "question_ar",
        "answer_ar",
        "source",
        "source_type",
    )
    for field in required_fields:
        if not str(question.get(field) or "").strip():
            debug_log("REJECTED", "Reason", f"missing {field}")
            raise ValueError(f"Invalid question: missing {field}")

    if question["difficulty"] not in VALID_DIFFICULTIES:
        debug_log("REJECTED", "Reason", f"invalid difficulty {question['difficulty']}")
        raise ValueError(f"Invalid question difficulty: {question['difficulty']}")
    if not is_valid_arabic_output(question["question_ar"]):
        debug_log("REJECTED", "Reason", "invalid Arabic question_ar")
        raise ValueError("Invalid question: question_ar is not valid Arabic output")
    if not is_valid_arabic_output(question["answer_ar"], allow_digits=True):
        debug_log("REJECTED", "Reason", "invalid Arabic answer_ar")
        raise ValueError("Invalid question: answer_ar is not valid Arabic output")

    question["points"] = int(question.get("points") or 200)
    question["metadata"] = _normalize_metadata(question.get("metadata") or {})
    if not str(question["metadata"].get("source_record_id") or "").strip():
        debug_log("REJECTED", "Reason", "missing metadata.source_record_id")
        raise ValueError("Invalid question: missing metadata.source_record_id")
    if question["metadata"]["display_mode"] == "reveal_visual":
        visual = question["metadata"].get("visual")
        if not isinstance(visual, dict) or not str(visual.get("type") or "").strip():
            debug_log("REJECTED", "Reason", "missing metadata.visual.type")
            raise ValueError("Invalid question: reveal_visual requires metadata.visual.type")
        if not str(visual.get("value") or visual.get("fallbackText") or "").strip():
            debug_log("REJECTED", "Reason", "missing metadata.visual value")
            raise ValueError("Invalid question: reveal_visual requires a visual value or fallbackText")
    question["needs_review"] = bool(question.get("needs_review"))
    debug_log("VALIDATION", "Question accepted", {"id": question["id"], "difficulty": question["difficulty"]})
    return question


def build_internal_question(
    *,
    question_id,
    category,
    difficulty,
    points,
    question_ar,
    answer_ar,
    source,
    source_type,
    metadata=None,
    needs_review=False,
) -> InternalQuestion:
    return validate_internal_question(
        {
            "id": question_id,
            "category": category,
            "difficulty": difficulty,
            "points": points,
            "question_ar": question_ar,
            "answer_ar": answer_ar,
            "source": source,
            "source_type": source_type,
            "metadata": metadata or {},
            "needs_review": needs_review,
        }
    )
