"""Purpose: generate the more descriptive country, travel, and aviation quiz variants."""

import random

from backend.api_adapters.rest_countries import get_country_context, translate_continent, translate_region, translate_weekday
from backend.services.generator_helpers import difficulty_pool, make_options, make_question, sample_distinct


def build_country_identify_questions(item, cache):
    countries = get_country_context(cache)
    questions = []
    configs = [("easy", 200), ("easy", 200), ("medium", 400), ("medium", 400), ("hard", 600), ("hard", 600)]

    def valid(country):
        return bool(country["capital"] and country["currency_codes"] and country["languages"])

    for index, (difficulty, points) in enumerate(configs, start=1):
        pool = difficulty_pool(countries, difficulty, valid)
        correct_country = random.choice(pool)
        language = correct_country["languages"][0]
        currency = correct_country["currency_codes"][0]
        continent = correct_country["continents"][0]
        text = f"ما هي الدولة التي عاصمتها {correct_country['capital']}، وعملة البلاد {currency}، وإحدى لغاتها الرسمية {language}؟"
        if difficulty != "easy":
            text = f"{text[:-1]}، وتقع في {continent}؟"

        distractors = [country["name"] for country in sample_distinct(pool, 8, {correct_country["cca3"]})]
        options, _ = make_options(correct_country["name"], distractors)
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


def build_country_travel_questions(item, cache):
    countries = get_country_context(cache)
    questions = []
    configs = [
        ("easy", 200, "destination_by_capital"),
        ("easy", 200, "destination_by_continent"),
        ("medium", 400, "destination_by_drive_side"),
        ("medium", 400, "destination_by_start_of_week"),
        ("hard", 600, "destination_by_timezone_and_capital"),
        ("hard", 600, "destination_by_landlocked_and_capital"),
    ]

    for index, (difficulty, points, mode) in enumerate(configs, start=1):
        pool = difficulty_pool(countries, difficulty, lambda country: bool(country["capital"] and country["continents"]))
        correct_country = random.choice(pool)
        answer = correct_country["name"]

        if mode == "destination_by_capital":
            text = f"إذا كانت رحلتك إلى مدينة {correct_country['capital']}، فأنت متجه إلى أي دولة؟"
            options, _ = make_options(answer, [country["name"] for country in sample_distinct(pool, 8, {correct_country["cca3"]})])
        elif mode == "destination_by_continent":
            text = f"أي دولة من التالية تُعد وجهة سفر في قارة {translate_continent(correct_country['continents'][0])}؟"
            options, _ = make_options(answer, [country["name"] for country in sample_distinct(pool, 8, {correct_country["cca3"]})])
        elif mode == "destination_by_drive_side":
            answer = "اليسار" if correct_country["car_side"] == "left" else "اليمين"
            text = f"إذا سافرت إلى {correct_country['name']}، ففي أي جهة من الطريق تقود السيارات غالبًا؟"
            options, _ = make_options(answer, ["اليسار", "اليمين"])
        elif mode == "destination_by_start_of_week":
            answer = translate_weekday(correct_country["start_of_week"] or "monday")
            text = f"في بيانات {correct_country['name']} يبدأ الأسبوع عادةً بأي يوم؟"
            options, _ = make_options(answer, ["الاثنين", "الأحد", "السبت", "الجمعة"])
        elif mode == "destination_by_timezone_and_capital":
            text = f"أي دولة عاصمتها {correct_country['capital']} وتسجل {len(correct_country['timezones'])} منطقة زمنية تقريبًا؟"
            options, _ = make_options(answer, [country["name"] for country in sample_distinct(pool, 8, {correct_country["cca3"]})])
        else:
            landlocked_copy = "دولة حبيسة" if correct_country["landlocked"] else "دولة ساحلية"
            text = f"أي دولة عاصمتها {correct_country['capital']} وتُعد {landlocked_copy}؟"
            options, _ = make_options(answer, [country["name"] for country in sample_distinct(pool, 8, {correct_country["cca3"]})])

        questions.append(make_question(f"{item['subcategoryId']}-{difficulty}-{index}", points, difficulty, text, answer, options))

    return questions


def build_country_aviation_questions(item, cache):
    countries = get_country_context(cache)
    questions = []
    configs = [
        ("easy", 200, "arrival_country"),
        ("easy", 200, "arrival_country"),
        ("medium", 400, "flight_continent"),
        ("medium", 400, "flight_timezone"),
        ("hard", 600, "flight_landlocked"),
        ("hard", 600, "flight_region_capital"),
    ]

    for index, (difficulty, points, mode) in enumerate(configs, start=1):
        pool = difficulty_pool(countries, difficulty, lambda country: bool(country["capital"] and country["continents"]))
        correct_country = random.choice(pool)

        if mode == "arrival_country":
            answer = correct_country["name"]
            text = f"إلى أي دولة تسافر إذا كانت وجهة رحلتك الجوية هي {correct_country['capital']}؟"
            options, _ = make_options(answer, [country["name"] for country in sample_distinct(pool, 8, {correct_country["cca3"]})])
        elif mode == "flight_continent":
            answer = translate_continent(correct_country["continents"][0])
            text = f"في أي قارة تهبط رحلتك إذا كانت وجهتك {correct_country['name']}؟"
            options, _ = make_options(answer, ["آسيا", "أفريقيا", "أوروبا", "أمريكا الشمالية", "أمريكا الجنوبية", "أوقيانوسيا"])
        elif mode == "flight_timezone":
            answer = str(len(correct_country["timezones"]))
            text = f"عند السفر إلى {correct_country['name']}، كم منطقة زمنية تقريبًا تُسجلها بيانات الوجهة؟"
            distractors = [str(number) for number in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12} if str(number) != answer]
            options, _ = make_options(answer, distractors)
        elif mode == "flight_landlocked":
            answer = "دولة حبيسة" if correct_country["landlocked"] else "دولة ساحلية"
            text = f"إذا كانت رحلتك إلى {correct_country['name']}، فهل وجهتك دولة حبيسة أم ساحلية؟"
            options, _ = make_options(answer, ["دولة حبيسة", "دولة ساحلية"])
        else:
            answer = correct_country["name"]
            text = f"أي دولة عاصمتها {correct_country['capital']} وتقع ضمن إقليم {translate_region(correct_country['region'])}؟"
            options, _ = make_options(answer, [country["name"] for country in sample_distinct(pool, 8, {correct_country["cca3"]})])

        questions.append(make_question(f"{item['subcategoryId']}-{difficulty}-{index}", points, difficulty, text, answer, options))

    return questions
