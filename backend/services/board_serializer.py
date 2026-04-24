"""Purpose: convert validated internal questions into the reveal-only frontend board shape."""

from backend.models.schemas import InternalQuestion
from backend.normalization.questions import validate_internal_question
from backend.utilities.debug import debug_log, debug_preview
from backend.utilities.text import icon_from_item


def serialize_question(question: InternalQuestion):
    debug_log("SERIALIZER", "Serializing internal question", question)
    question = validate_internal_question(dict(question))
    metadata = question.get("metadata") or {}
    # Keep the frontend payload reveal-only (no MCQ fields) and preserve visual
    # metadata for logo/flag categories without leaking extra source-side blobs.
    visual = metadata.get("visual")

    payload = {
        "id": question.get("id"),
        "points": int(question.get("points") or 200),
        "difficulty": question.get("difficulty"),
        "question": question.get("question_ar"),
        "answer": question.get("answer_ar"),
        "displayMode": metadata.get("display_mode", "reveal_answer"),
        "source": question.get("source"),
        "sourceType": question.get("source_type"),
        "metadata": metadata,
    }
    if metadata.get("question_type"):
        payload["questionType"] = metadata["question_type"]
    if isinstance(visual, dict):
        payload["visual"] = visual
    debug_log("SERIALIZER", "Serialized question payload", payload)
    return payload


def serialize_category(selection, source_definition, internal_questions):
    debug_log(
        "SERIALIZER",
        f'Serializing category "{selection["backend_category"]}"',
        debug_preview(internal_questions, limit=6),
    )
    question_sources = sorted(
        {
            str(question.get("source") or "").strip()
            for question in internal_questions
            if str(question.get("source") or "").strip()
        }
    )
    serialized = {
        "id": selection["ui_subcategory_id"],
        "name": selection["ui_title_ar"],
        "backendCategory": selection["backend_category"],
        "icon": icon_from_item({"iconKey": selection.get("iconKey")}),
        "imageKey": selection.get("imageKey"),
        "iconKey": selection.get("iconKey"),
        "flagCode": selection.get("flagCode"),
        "description": f"أسئلة reveal مجهزة حيًا من مصدر {source_definition['source']}.",
        "questions": [serialize_question(question) for question in internal_questions],
        "sourceMode": "api",
        "resolvedSource": " + ".join(question_sources) if question_sources else source_definition["source"],
        "sourceType": source_definition["source_type"],
    }
    debug_log("SERIALIZER", "Final payload", serialized)
    return serialized
