"""Purpose: generate the smaller core set of country quiz question variants."""

import random

from backend.api_adapters.rest_countries import (
    get_country_context,
    translate_continent,
    translate_region,
    translate_subregion,
)
from backend.services.generator_helpers import difficulty_pool, make_options, make_question, sample_distinct


def build_country_capitals_questions(item, cache):
    countries = get_country_context(cache)
    questions = []
    configs = [("easy", 200), ("easy", 200), ("medium", 400), ("medium", 400), ("hard", 600), ("hard", 600)]

    for index, (difficulty, points) in enumerate(configs, start=1):
        pool = difficulty_pool(countries, difficulty, lambda country: bool(country["capital"]))
        correct_country = random.choice(pool)
        correct_answer = correct_country["name"]
        distractors = [country["name"] for country in sample_distinct(pool, 6, {correct_country["cca3"]})]
        options, _ = make_options(correct_answer, distractors)
        text = f"عاصمة أي دولة هي {correct_country['capital']}؟"
        questions.append(
            make_question(
                f"{item['subcategoryId']}-{difficulty}-{index}",
                points,
                difficulty,
                text,
                correct_answer,
                options,
            )
        )

    return questions


def build_country_flags_questions(item, cache):
    countries = get_country_context(cache)
    questions = []
    configs = [("easy", 200), ("easy", 200), ("medium", 400), ("medium", 400), ("hard", 600), ("hard", 600)]

    for index, (difficulty, points) in enumerate(configs, start=1):
        pool = difficulty_pool(countries, difficulty, lambda country: bool(country["flag"]))
        correct_country = random.choice(pool)
        distractors = [country["name"] for country in sample_distinct(pool, 6, {correct_country["cca3"]})]
        options, _ = make_options(correct_country["name"], distractors)
        questions.append(
            make_question(
                f"{item['subcategoryId']}-{difficulty}-{index}",
                points,
                difficulty,
                "لأي دولة يعود هذا العلم؟",
                correct_country["name"],
                options,
                {"visual": {"type": "flag", "value": correct_country["flag"]}},
            )
        )

    return questions


def build_country_currency_questions(item, cache):
    countries = get_country_context(cache)
    questions = []
    configs = [("easy", 200), ("easy", 200), ("medium", 400), ("medium", 400), ("hard", 600), ("hard", 600)]

    for index, (difficulty, points) in enumerate(configs, start=1):
        pool = difficulty_pool(countries, difficulty, lambda country: bool(country["currency_codes"]))
        correct_country = random.choice(pool)
        currency_code = correct_country["currency_codes"][0]
        distractors = [country["name"] for country in sample_distinct(pool, 8, {correct_country["cca3"]})]
        options, _ = make_options(correct_country["name"], distractors)
        text = f"أي دولة تستخدم العملة ذات الرمز {currency_code}؟"
        questions.append(
            make_question(
                f"{item['subcategoryId']}-{difficulty}-{index}",
                points,
                difficulty,
                text,
                correct_country["name"],
                options,
            )
        )

    return questions


def build_country_language_questions(item, cache):
    countries = get_country_context(cache)
    questions = []
    configs = [
        ("easy", 200, "country_of_language"),
        ("easy", 200, "country_of_language"),
        ("medium", 400, "country_of_language"),
        ("hard", 600, "identify_from_language_and_capital"),
        ("hard", 600, "identify_from_language_and_region"),
        ("medium", 400, "identify_from_language_and_capital"),
    ]

    for index, (difficulty, points, mode) in enumerate(configs, start=1):
        pool = difficulty_pool(countries, difficulty, lambda country: bool(country["languages"]))
        correct_country = random.choice(pool)
        language = correct_country["languages"][0]
        distractors = [country["name"] for country in sample_distinct(pool, 8, {correct_country["cca3"]})]
        options, _ = make_options(correct_country["name"], distractors)

        if mode == "country_of_language":
            text = f"في أي دولة تُعد {language} لغة رسمية؟"
        elif mode == "identify_from_language_and_capital":
            text = f"ما الدولة التي عاصمتها {correct_country['capital']} وإحدى لغاتها الرسمية {language}؟"
        else:
            region = translate_region(correct_country["region"])
            text = f"أي دولة تقع في {region} وتُعد {language} لغة رسمية فيها؟"

        questions.append(
            make_question(
                f"{item['subcategoryId']}-{difficulty}-{index}",
                points,
                difficulty,
                text,
                correct_country["name"],
                options,
            )
        )

    return questions


def build_country_geography_questions(item, cache):
    countries = get_country_context(cache)
    questions = []
    configs = [
        ("easy", 200, "continent"),
        ("easy", 200, "region"),
        ("medium", 400, "subregion"),
        ("medium", 400, "borders_count"),
        ("hard", 600, "landlocked"),
        ("hard", 600, "timezone_count"),
    ]

    for index, (difficulty, points, mode) in enumerate(configs, start=1):
        pool = difficulty_pool(countries, difficulty, lambda country: bool(country["continents"]))
        correct_country = random.choice(pool)

        if mode == "continent":
            answer = translate_continent(correct_country["continents"][0])
            text = f"في أي قارة تقع {correct_country['name']}؟"
            options, _ = make_options(answer, ["آسيا", "أفريقيا", "أوروبا", "أمريكا الشمالية", "أمريكا الجنوبية", "أوقيانوسيا"])
        elif mode == "region":
            answer = translate_region(correct_country["region"])
            text = f"إلى أي إقليم رئيسي تنتمي {correct_country['name']}؟"
            options, _ = make_options(answer, ["أفريقيا", "الأمريكيتان", "آسيا", "أوروبا", "أوقيانوسيا", "القطب"])
        elif mode == "subregion":
            pool = [country for country in pool if country["subregion"]]
            correct_country = random.choice(pool)
            answer = translate_subregion(correct_country["subregion"])
            distractors = [translate_subregion(country["subregion"]) for country in sample_distinct(pool, 8, {correct_country["cca3"]}) if country["subregion"]]
            text = f"ما المنطقة الفرعية التي تقع فيها {correct_country['name']}؟"
            options, _ = make_options(answer, distractors)
        elif mode == "borders_count":
            answer = str(len(correct_country["borders"]))
            distractors = [str(number) for number in {0, 1, 2, 3, 4, 5, 6, 7, 8, 9} if str(number) != answer]
            text = f"كم عدد الدول التي تشترك بحدود برية مع {correct_country['name']}؟"
            options, _ = make_options(answer, distractors)
        elif mode == "landlocked":
            landlocked_pool = [country for country in pool if country["landlocked"]]
            coast_pool = [country for country in pool if not country["landlocked"]]
            if not landlocked_pool or len(coast_pool) < 3:
                return build_country_geography_questions(item, {"countries": countries})
            correct_country = random.choice(landlocked_pool)
            answer = correct_country["name"]
            text = "أي دولة من التالية دولة حبيسة لا تطل على بحر؟"
            options, _ = make_options(answer, [country["name"] for country in sample_distinct(coast_pool, 3)])
        else:
            answer = str(len(correct_country["timezones"]))
            distractors = [str(number) for number in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12} if str(number) != answer]
            text = f"كم منطقة زمنية تقريبًا تسجلها بيانات {correct_country['name']}؟"
            options, _ = make_options(answer, distractors)

        questions.append(make_question(f"{item['subcategoryId']}-{difficulty}-{index}", points, difficulty, text, answer, options))

    return questions
