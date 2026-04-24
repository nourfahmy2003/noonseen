"""Purpose: share small quiz-construction helpers across generator modules."""

import random


MIN_POPULATION_BY_DIFFICULTY = {
    "easy": 5_000_000,
    "medium": 1_500_000,
    "hard": 350_000,
}

EXCLUDED_TERRITORY_CODES = {
    "AI", "AS", "AW", "BL", "BM", "BQ", "BV", "CC", "CK", "CW", "FK", "FO",
    "GF", "GG", "GI", "GL", "GP", "GU", "HK", "IM", "JE", "KY", "MF", "MQ",
    "MS", "NC", "NF", "NU", "PF", "PM", "PN", "PR", "RE", "SH", "SJ", "SX",
    "TC", "TK", "VI", "WF", "YT",
}


def _is_country_eligible(country, difficulty):
    if not isinstance(country, dict):
        return True
    if "population" not in country or "cca3" not in country:
        return True
    if country.get("cca2") in EXCLUDED_TERRITORY_CODES:
        return False

    independent = country.get("independent")
    un_member = country.get("un_member")
    if independent is False and un_member is False:
        return False
    return int(country.get("population") or 0) >= MIN_POPULATION_BY_DIFFICULTY.get(difficulty, 0)


def difficulty_pool(countries, difficulty, predicate=None):
    filtered = [
        country
        for country in countries
        if _is_country_eligible(country, difficulty) and (predicate(country) if predicate else True)
    ]
    if not filtered:
        filtered = [country for country in countries if (predicate(country) if predicate else True)]
    if not filtered:
        return []

    if difficulty == "easy":
        pool = filtered[: min(70, len(filtered))]
    elif difficulty == "medium":
        pool = filtered[40 : min(140, len(filtered))]
    else:
        pool = filtered[100:] if len(filtered) > 100 else filtered[-60:]

    return pool or filtered


def pick_unique_item(items, used_keys, key_fn):
    available = [item for item in items if key_fn(item) not in used_keys]
    choice = random.choice(available or items)
    used_keys.add(key_fn(choice))
    return choice


def sample_distinct(items, amount, exclude=None):
    def identity(value):
        if isinstance(value, dict):
            return value.get("cca3") or value.get("cca2") or value.get("name")
        return value

    exclude_keys = {identity(item) for item in (exclude or [])}
    filtered = [item for item in items if identity(item) not in exclude_keys]
    if len(filtered) <= amount:
        return filtered
    return random.sample(filtered, amount)


def make_options(correct, distractors, minimum=4):
    options = [correct]
    for item in distractors:
        if item and item not in options:
            options.append(item)
        if len(options) >= minimum:
            break

    while len(options) < minimum:
        options.append(f"خيار {len(options) + 1}")

    random.shuffle(options)
    return options, options.index(correct)


def make_question(question_id, points, difficulty, text, answer, options, extras=None):
    payload = {
        "id": question_id,
        "points": points,
        "difficulty": difficulty,
        "question": text,
        "answer": answer,
        "options": options,
        "correctIndex": options.index(answer),
    }
    if extras:
        payload.update(extras)
    return payload
