"""Purpose: build the descriptive REST Countries reveal-mode variants for travel, identify-country, and languages."""

from backend.api_adapters.rest_countries import get_country_context, translate_continent, translate_region
from backend.arabic.transform import ensure_arabic_label
from backend.services.generator_helpers import difficulty_pool, pick_unique_item
from backend.source_clients.rest_countries_core import _build_question
from backend.utilities.debug import debug_log
from backend.utilities.ids import source_record_id


def build_country_identify_questions(selection, source_definition, difficulty_slots, countries=None, cache=None):
    countries = countries or get_country_context(cache or {})
    prepared = []
    used_codes = set()
    for difficulty, points in difficulty_slots:
        pool = difficulty_pool(
            countries,
            difficulty,
            lambda country: bool(country["capital"] and country["currency_codes"] and country["languages"]),
        )
        correct = pick_unique_item(pool, used_codes, lambda country: country["cca3"])
        debug_log("RAW RECORD", "Incoming data", correct)
        capital_ar, capital_review = ensure_arabic_label(correct["capital"])
        language_ar, language_review = ensure_arabic_label(correct["languages"][0])
        # Prefer the visible currency name over the code so the clue reads
        # naturally in Arabic when the source data provides it.
        currency_value = correct["currency_names"][0] if correct["currency_names"] else correct["currency_codes"][0]
        currency_ar, currency_review = ensure_arabic_label(currency_value)
        clue_parts = [f"عاصمتها {capital_ar}"]
        if not currency_review:
            clue_parts.append(f"عملتها {currency_ar}")
        if not language_review:
            clue_parts.append(f"إحدى لغاتها الرسمية {language_ar}")

        continent_ar = translate_continent(correct["continents"][0])
        region_ar = translate_region(correct["region"])
        if difficulty != "easy" or len(clue_parts) < 2:
            clue_parts.append(f"تقع في {continent_ar}")
        if difficulty == "hard" and len(clue_parts) < 3:
            clue_parts.append(f"ضمن إقليم {region_ar}")

        question = f"ما هي الدولة التي {' و'.join(clue_parts)}؟"
        prepared.append(
            _build_question(
                selection,
                source_definition,
                record_id=source_record_id("restcountries", "identify", correct["cca3"], difficulty),
                difficulty=difficulty,
                points=points,
                question_ar=question,
                answer_ar=correct["name"],
                needs_review=capital_review or language_review or currency_review,
                metadata={
                    "capital": capital_ar,
                    "language": language_ar,
                    "currency": currency_ar,
                    "continent": continent_ar,
                    "region": region_ar,
                    "display_mode": "reveal_answer",
                },
            )
        )
    return prepared


def build_country_languages_questions(selection, source_definition, countries=None, cache=None):
    countries = countries or get_country_context(cache or {})
    configs = (
        ("easy", 200, "country_of_language"),
        ("easy", 200, "country_of_language"),
        ("medium", 400, "country_of_language"),
        ("medium", 400, "capital_and_language"),
        ("hard", 600, "region_and_language"),
        ("hard", 600, "capital_and_language"),
    )
    prepared = []
    used_codes = set()
    for difficulty, points, mode in configs:
        pool = difficulty_pool(
            countries,
            difficulty,
            lambda country: bool(country["languages"] and (country["capital"] if mode == "capital_and_language" else True)),
        )
        correct = pick_unique_item(pool, used_codes, lambda country: country["cca3"])
        debug_log("RAW RECORD", "Incoming data", correct)
        language_ar, needs_review = ensure_arabic_label(correct["languages"][0])
        if mode == "country_of_language":
            question = f"في أي دولة تُعد {language_ar} لغة رسمية؟"
        elif mode == "capital_and_language":
            capital_ar, capital_review = ensure_arabic_label(correct["capital"])
            question = f"ما الدولة التي عاصمتها {capital_ar} وإحدى لغاتها الرسمية {language_ar}؟"
            needs_review = needs_review or capital_review
        else:
            region_ar, region_review = ensure_arabic_label(translate_region(correct["region"]))
            question = f"أي دولة تقع في {region_ar} وتُعد {language_ar} لغة رسمية فيها؟"
            needs_review = needs_review or region_review
        prepared.append(
            _build_question(
                selection,
                source_definition,
                record_id=source_record_id("restcountries", mode, correct["cca3"], difficulty),
                difficulty=difficulty,
                points=points,
                question_ar=question,
                answer_ar=correct["name"],
                needs_review=needs_review,
                metadata={"language": language_ar, "display_mode": "reveal_answer"},
            )
        )
    return prepared


def build_country_travel_questions(selection, source_definition, countries=None, cache=None):
    countries = countries or get_country_context(cache or {})
    configs = (
        ("easy", 200, "destination_by_capital"),
        ("easy", 200, "destination_by_continent"),
        ("medium", 400, "destination_by_drive_side"),
        ("medium", 400, "destination_by_start_of_week"),
        ("hard", 600, "destination_by_timezone_and_capital"),
        ("hard", 600, "destination_by_landlocked_and_capital"),
    )
    prepared = []
    used_codes = set()
    for difficulty, points, mode in configs:
        pool = difficulty_pool(
            countries,
            difficulty,
            lambda country: bool(country["capital"] and country["continents"]),
        )
        correct = pick_unique_item(pool, used_codes, lambda country: country["cca3"])
        debug_log("RAW RECORD", "Incoming data", correct)
        needs_review = False
        if mode == "destination_by_capital":
            capital_ar, needs_review = ensure_arabic_label(correct["capital"])
            question = f"إذا كانت رحلتك إلى مدينة {capital_ar}، فأنت متجه إلى أي دولة؟"
            answer = correct["name"]
        elif mode == "destination_by_continent":
            question = f"أي دولة من التالية تُعد وجهة سفر في قارة {translate_continent(correct['continents'][0])}؟"
            answer = correct["name"]
        elif mode == "destination_by_drive_side":
            question = f"إذا سافرت إلى {correct['name']}، ففي أي جهة من الطريق تقود السيارات غالبًا؟"
            answer = "اليسار" if correct["car_side"] == "left" else "اليمين"
        elif mode == "destination_by_start_of_week":
            question = f"في بيانات {correct['name']} يبدأ الأسبوع عادةً بأي يوم؟"
            answer = (
                "الاثنين" if correct["start_of_week"] == "monday"
                else "الأحد" if correct["start_of_week"] == "sunday"
                else "السبت" if correct["start_of_week"] == "saturday"
                else "الجمعة"
            )
        elif mode == "destination_by_timezone_and_capital":
            capital_ar, needs_review = ensure_arabic_label(correct["capital"])
            question = f"أي دولة عاصمتها {capital_ar} وتسجل {len(correct['timezones'])} منطقة زمنية تقريبًا؟"
            answer = correct["name"]
        else:
            capital_ar, needs_review = ensure_arabic_label(correct["capital"])
            question = f"أي دولة عاصمتها {capital_ar} وتُعد {'دولة حبيسة' if correct['landlocked'] else 'دولة ساحلية'}؟"
            answer = correct["name"]
        prepared.append(
            _build_question(
                selection,
                source_definition,
                record_id=source_record_id("restcountries", mode, correct["cca3"], difficulty),
                difficulty=difficulty,
                points=points,
                question_ar=question,
                answer_ar=answer,
                needs_review=needs_review,
                metadata={"display_mode": "reveal_answer"},
            )
        )
    return prepared


def build_country_aviation_questions(selection, source_definition, countries=None, cache=None):
    countries = countries or get_country_context(cache or {})
    configs = (
        ("easy", 200, "arrival_country"),
        ("easy", 200, "arrival_country"),
        ("medium", 400, "flight_continent"),
        ("medium", 400, "flight_timezone"),
        ("hard", 600, "flight_landlocked"),
        ("hard", 600, "flight_region_capital"),
    )
    prepared = []
    used_codes = set()
    for difficulty, points, mode in configs:
        pool = difficulty_pool(countries, difficulty, lambda country: bool(country["capital"] and country["continents"]))
        correct = pick_unique_item(pool, used_codes, lambda country: country["cca3"])
        debug_log("RAW RECORD", "Incoming data", correct)
        needs_review = False
        if mode == "arrival_country":
            capital_ar, needs_review = ensure_arabic_label(correct["capital"])
            question = f"إلى أي دولة تسافر إذا كانت وجهة رحلتك الجوية هي {capital_ar}؟"
            answer = correct["name"]
        elif mode == "flight_continent":
            question = f"في أي قارة تهبط رحلتك إذا كانت وجهتك {correct['name']}؟"
            answer = translate_continent(correct["continents"][0])
        elif mode == "flight_timezone":
            question = f"عند السفر إلى {correct['name']}، كم منطقة زمنية تقريبًا تُسجلها بيانات الوجهة؟"
            answer = str(len(correct["timezones"]))
        elif mode == "flight_landlocked":
            question = f"إذا كانت رحلتك إلى {correct['name']}، فهل وجهتك دولة حبيسة أم ساحلية؟"
            answer = "دولة حبيسة" if correct["landlocked"] else "دولة ساحلية"
        else:
            capital_ar, needs_review = ensure_arabic_label(correct["capital"])
            question = f"أي دولة عاصمتها {capital_ar} وتقع ضمن إقليم {translate_region(correct['region'])}؟"
            answer = correct["name"]
        prepared.append(
            _build_question(
                selection,
                source_definition,
                record_id=source_record_id("restcountries", mode, correct["cca3"], difficulty),
                difficulty=difficulty,
                points=points,
                question_ar=question,
                answer_ar=answer,
                needs_review=needs_review,
                metadata={"display_mode": "reveal_answer"},
            )
        )
    return prepared
