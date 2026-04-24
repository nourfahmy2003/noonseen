"""Purpose: build the core REST Countries reveal-mode variants for capitals, currencies, flags, and geography."""

import random

from backend.api_adapters.rest_countries import (
    get_country_context,
    translate_continent,
    translate_region,
    translate_subregion,
)
from backend.arabic.transform import ensure_arabic_label
from backend.normalization.questions import build_internal_question
from backend.services.generator_helpers import difficulty_pool, pick_unique_item
from backend.utilities.debug import debug_log
from backend.utilities.ids import source_record_id


def _build_question(
    selection,
    source_definition,
    *,
    record_id,
    difficulty,
    points,
    question_ar,
    answer_ar,
    needs_review=False,
    metadata=None,
):
    debug_log(
        "VALIDATION",
        "Checking question",
        {"question": question_ar, "answer": answer_ar, "difficulty": difficulty, "record_id": record_id},
    )
    debug_log(
        "TRANSFORM",
        "Built question",
        {"question_ar": question_ar, "answer_ar": answer_ar, "difficulty": difficulty, "metadata": metadata or {}},
    )
    return build_internal_question(
        question_id=record_id,
        category=selection["backend_category"],
        difficulty=difficulty,
        points=points,
        question_ar=question_ar,
        answer_ar=answer_ar,
        source=source_definition["source"],
        source_type=source_definition["source_type"],
        metadata={"source_record_id": record_id, **(metadata or {})},
        needs_review=needs_review,
    )


def build_country_capitals_questions(selection, source_definition, difficulty_slots, countries=None, cache=None):
    countries = countries or get_country_context(cache or {})
    prepared = []
    used_codes = set()
    for difficulty, points in difficulty_slots:
        pool = difficulty_pool(
            countries,
            difficulty,
            lambda country: bool(country["capital"]) and not ensure_arabic_label(country["capital"])[1],
        )
        correct = pick_unique_item(pool, used_codes, lambda country: country["cca3"])
        debug_log("RAW RECORD", "Incoming data", correct)
        capital_ar, needs_review = ensure_arabic_label(correct["capital"])
        currency_code = correct["currency_codes"][0] if correct["currency_codes"] else ""
        region_ar = translate_region(correct["region"])
        if difficulty == "easy":
            question = f"ما الدولة التي عاصمتها {capital_ar}؟"
        elif difficulty == "medium":
            question = f"ما الدولة التي عاصمتها {capital_ar} وتقع ضمن إقليم {region_ar}؟"
        else:
            question = f"ما الدولة التي عاصمتها {capital_ar} وتستخدم العملة ذات الرمز {currency_code}؟"
        prepared.append(
            _build_question(
                selection,
                source_definition,
                record_id=source_record_id("restcountries", "capital", correct["cca3"], difficulty),
                difficulty=difficulty,
                points=points,
                question_ar=question,
                answer_ar=correct["name"],
                needs_review=needs_review,
                metadata={"capital": capital_ar, "currency_code": currency_code, "region": region_ar, "display_mode": "reveal_answer"},
            )
        )
    return prepared


def build_country_currencies_questions(selection, source_definition, difficulty_slots, countries=None, cache=None):
    countries = countries or get_country_context(cache or {})
    prepared = []
    used_codes = set()
    for difficulty, points in difficulty_slots:
        pool = difficulty_pool(
            countries,
            difficulty,
            lambda country: bool(country["currency_codes"] and country["currency_names"] and country["capital"]),
        )
        correct = pick_unique_item(pool, used_codes, lambda country: country["cca3"])
        debug_log("RAW RECORD", "Incoming data", correct)
        currency_name = correct["currency_names"][0] if correct["currency_names"] else correct["currency_codes"][0]
        currency_ar, needs_review = ensure_arabic_label(currency_name)
        capital_ar, capital_review = ensure_arabic_label(correct["capital"])
        region_ar = translate_region(correct["region"])
        question = (
            "ما العملة الرسمية للدولة التي يظهر علمها؟"
            if difficulty == "easy"
            else f"ما العملة الرسمية للدولة التي عاصمتها {capital_ar}؟"
            if difficulty == "medium"
            else f"ما العملة الرسمية للدولة التي عاصمتها {capital_ar} وتقع ضمن إقليم {region_ar}؟"
        )
        prepared.append(
            _build_question(
                selection,
                source_definition,
                record_id=source_record_id("restcountries", "currency", correct["cca3"], difficulty),
                difficulty=difficulty,
                points=points,
                question_ar=question,
                answer_ar=currency_ar,
                needs_review=needs_review or capital_review,
                metadata={
                    "currency": currency_ar,
                    "currency_code": correct["currency_codes"][0],
                    "capital": capital_ar,
                    "visual": {"type": "flag-image", "value": correct["flag_svg"]},
                    "display_mode": "reveal_answer",
                },
            )
        )
    return prepared


def build_country_geography_questions(selection, source_definition, countries=None, cache=None):
    countries = countries or get_country_context(cache or {})
    configs = (
        ("easy", 200, "continent"),
        ("easy", 200, "region"),
        ("medium", 400, "subregion"),
        ("medium", 400, "borders"),
        ("hard", 600, "timezone_count"),
        ("hard", 600, "landlocked"),
    )
    prepared = []
    for difficulty, points, mode in configs:
        pool = difficulty_pool(countries, difficulty, lambda country: bool(country["continents"]))
        correct = random.choice(pool)
        debug_log("RAW RECORD", "Incoming data", correct)
        if mode == "continent":
            question = f"في أي قارة تقع {correct['name']}؟"
            answer = translate_continent(correct["continents"][0])
        elif mode == "region":
            question = f"إلى أي إقليم رئيسي تنتمي {correct['name']}؟"
            answer = translate_region(correct["region"])
        elif mode == "subregion":
            pool = [country for country in pool if country["subregion"]]
            correct = random.choice(pool)
            question = f"ما المنطقة الفرعية التي تقع فيها {correct['name']}؟"
            answer = translate_subregion(correct["subregion"])
        elif mode == "borders":
            question = f"كم عدد الدول التي تشترك بحدود برية مع {correct['name']}؟"
            answer = str(len(correct["borders"]))
        elif mode == "timezone_count":
            question = f"كم منطقة زمنية تقريبًا تسجلها بيانات {correct['name']}؟"
            answer = str(len(correct["timezones"]))
        else:
            question = f"هل تُعد {correct['name']} دولة حبيسة أم ساحلية؟"
            answer = "دولة حبيسة" if correct["landlocked"] else "دولة ساحلية"
        prepared.append(
            _build_question(
                selection,
                source_definition,
                record_id=source_record_id("restcountries", mode, correct["cca3"], difficulty),
                difficulty=difficulty,
                points=points,
                question_ar=question,
                answer_ar=answer,
                metadata={"display_mode": "reveal_answer"},
            )
        )
    return prepared


def build_country_flags_questions(selection, source_definition, difficulty_slots, countries=None, cache=None):
    countries = countries or get_country_context(cache or {})
    prepared = []
    used_codes = set()
    for difficulty, points in difficulty_slots:
        pool = difficulty_pool(countries, difficulty, lambda country: bool(country["flag"] or country["flag_svg"]))
        correct = pick_unique_item(pool, used_codes, lambda country: country["cca3"])
        debug_log("RAW RECORD", "Incoming data", correct)
        prepared.append(
            _build_question(
                selection,
                source_definition,
                record_id=source_record_id("restcountries", "flag", correct["cca3"], difficulty),
                difficulty=difficulty,
                points=points,
                question_ar="لأي دولة يعود هذا العلم؟",
                answer_ar=correct["name"],
                metadata={
                    "visual": {"type": "flag-image" if correct["flag_svg"] else "flag", "value": correct["flag_svg"] or correct["flag"]},
                    "display_mode": "reveal_visual",
                },
            )
        )
    return prepared
