"""Purpose: dispatch REST Countries-backed categories to focused question builders."""

from backend.api_adapters.rest_countries import get_country_context
from backend.difficulty.rules import iter_difficulty_slots
from backend.source_clients.rest_countries_core import (
    build_country_capitals_questions,
    build_country_currencies_questions,
    build_country_flags_questions,
    build_country_geography_questions,
)
from backend.source_clients.rest_countries_extended import (
    build_country_aviation_questions,
    build_country_identify_questions,
    build_country_languages_questions,
    build_country_travel_questions,
)
from backend.utilities.debug import debug_log, debug_preview


def fetch_questions(selection, source_definition, cache):
    countries = get_country_context(cache)
    difficulty_slots = iter_difficulty_slots()
    category = selection["backend_category"]
    debug_log("CATEGORY", f'Processing: "{category}"', {"country_count": len(countries)})

    # Accept both historical UI spellings so old selections still resolve to
    # the live country-capitals generator.
    if category in {"دول وعواصم", "دول و عواصم"}:
        prepared = build_country_capitals_questions(selection, source_definition, difficulty_slots, countries=countries)
    elif category == "أعلام":
        prepared = build_country_flags_questions(selection, source_definition, difficulty_slots, countries=countries)
    elif category == "ما هي الدولة":
        prepared = build_country_identify_questions(selection, source_definition, difficulty_slots, countries=countries)
    elif category == "سياحة وسفر":
        prepared = build_country_travel_questions(selection, source_definition, countries=countries)
    elif category == "عالم الطيران":
        prepared = build_country_aviation_questions(selection, source_definition, countries=countries)
    elif category == "لغات ولهجات":
        prepared = build_country_languages_questions(selection, source_definition, countries=countries)
    elif category == "عملات":
        prepared = build_country_currencies_questions(selection, source_definition, difficulty_slots, countries=countries)
    else:
        prepared = build_country_geography_questions(selection, source_definition, countries=countries)
    debug_log("FINAL", "Questions ready", debug_preview(prepared, limit=5))
    return prepared
