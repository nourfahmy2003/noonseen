"""Purpose: prepare the match question bank from live sources only with clear diagnostics.

There is intentionally no local JSON bank here: failures bubble up as diagnostics so hosts
can see which live dependency (API keys, LibreTranslate, upstream trivia) needs attention.
"""

from backend.services.board_serializer import serialize_category
from backend.services.category_mapping import (
    expand_grouped_selected_items,
    get_unavailable_reason,
    map_selected_subcategory,
)
from backend.source_clients.alquran_cloud import fetch_questions as fetch_alquran_cloud_questions
from backend.source_clients.api_ninjas_logo import fetch_questions as fetch_api_ninjas_logo_questions
from backend.source_clients.islamic_quiz_api import fetch_questions as fetch_islamic_quiz_api_questions
from backend.source_clients.kalimalab import fetch_questions as fetch_kalimalab_questions
from backend.source_clients.open_trivia import fetch_questions as fetch_open_trivia_questions
from backend.source_clients.rest_countries import fetch_questions as fetch_rest_countries_questions
from backend.source_clients.the_trivia import fetch_questions as fetch_the_trivia_questions
from backend.source_registry import get_source_definition, has_live_source_definition
from backend.utilities.debug import debug_log, debug_preview


SOURCE_CLIENTS = {
    "kalimalab": fetch_kalimalab_questions,
    "alquran_cloud": fetch_alquran_cloud_questions,
    "the_trivia": fetch_the_trivia_questions,
    "open_trivia": fetch_open_trivia_questions,
    "rest_countries": fetch_rest_countries_questions,
    "islamic_quiz_api": fetch_islamic_quiz_api_questions,
    "api_ninjas_logo": fetch_api_ninjas_logo_questions,
}


def _resolve_questions(selection, source_definition, cache):
    debug_log(
        "SOURCE",
        f'Category "{selection["backend_category"]}" → using {source_definition["client_key"]}',
        source_definition,
    )
    primary_client = SOURCE_CLIENTS[source_definition["client_key"]]
    internal_questions = primary_client(selection, source_definition, cache)
    debug_log(
        "FINAL",
        f'Validated internal questions for "{selection["backend_category"]}"',
        debug_preview(internal_questions, limit=5),
    )
    if len(internal_questions) != 6:
        raise ValueError(f"{selection['backend_category']} must return exactly 6 validated live questions")
    return internal_questions, source_definition


def prepare_match_question_bank(selected_items):
    cache = {}
    categories = []
    diagnostics = []
    resolved_items = expand_grouped_selected_items(selected_items)
    debug_log("CATEGORY", "Selected from UI", debug_preview(selected_items, limit=10))
    debug_log("CATEGORY", "Expanded selected items", debug_preview(resolved_items, limit=10))

    for item in resolved_items:
        selection = map_selected_subcategory(item)
        source_definition = get_source_definition(selection["backend_category"])
        debug_log(
            "CATEGORY",
            "Mapped backend categories",
            {
                "ui_subcategory_id": selection["ui_subcategory_id"],
                "ui_title_ar": selection["ui_title_ar"],
                "backend_category": selection["backend_category"],
            },
        )
        debug_log("CATEGORY", f'Processing: "{selection["backend_category"]}"', selection)

        if selection["backend_category"] == "needs_label_confirmation":
            debug_log(
                "REJECTED",
                "Category is unavailable pending label confirmation",
                selection["backend_category"],
            )
            diagnostics.append(
                {
                    "id": selection["ui_subcategory_id"],
                    "name": selection["ui_title_ar"],
                    "backendCategory": selection["backend_category"],
                    "sourceMode": "unavailable",
                    "questionCount": 0,
                    "source": "needs_label_confirmation",
                    "sourceType": "unavailable",
                    "reason": get_unavailable_reason(selection["backend_category"]),
                }
            )
            continue

        if not source_definition or not has_live_source_definition(selection["backend_category"]):
            debug_log(
                "REJECTED",
                "Category has no live source definition",
                {
                    "backend_category": selection["backend_category"],
                    "source_definition": source_definition,
                },
            )
            diagnostics.append(
                {
                    "id": selection["ui_subcategory_id"],
                    "name": selection["ui_title_ar"],
                    "backendCategory": selection["backend_category"],
                    "sourceMode": "unavailable",
                    "questionCount": 0,
                    "source": source_definition["source"] if source_definition else "not_configured",
                    "sourceType": source_definition["source_type"] if source_definition else "unavailable",
                    "reason": get_unavailable_reason(selection["backend_category"]),
                }
            )
            continue

        try:
            internal_questions, resolved_source = _resolve_questions(selection, source_definition, cache)
            category = serialize_category(selection, resolved_source, internal_questions)
            categories.append(category)
            debug_log(
                "FINAL",
                f'Category ready for frontend: "{selection["backend_category"]}"',
                debug_preview(category, limit=5),
            )
            diagnostics.append(
                {
                    "id": selection["ui_subcategory_id"],
                    "name": selection["ui_title_ar"],
                    "backendCategory": selection["backend_category"],
                    "sourceMode": "api",
                    "questionCount": len(category["questions"]),
                    "source": resolved_source["source"],
                    "sourceType": resolved_source["source_type"],
                }
            )
        except Exception as error:
            debug_log(
                "API ERROR",
                f'Question preparation failed for "{selection["backend_category"]}"',
                str(error),
            )
            diagnostics.append(
                {
                    "id": selection["ui_subcategory_id"],
                    "name": selection["ui_title_ar"],
                    "backendCategory": selection["backend_category"],
                    "sourceMode": "failed",
                    "questionCount": 0,
                    "source": source_definition["source"],
                    "sourceType": source_definition["source_type"],
                    "reason": str(error),
                }
            )

    debug_log("FINAL", "Questions ready", debug_preview(categories, limit=5))
    debug_log("FINAL", "Diagnostics ready", debug_preview(diagnostics, limit=10))
    return categories, diagnostics
