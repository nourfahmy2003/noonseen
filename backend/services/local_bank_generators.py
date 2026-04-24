"""Purpose: generate quiz questions directly from localized general and country banks."""

from backend.data.country_bank import COUNTRY_CATEGORY_BANK
from backend.data.general_bank import GENERAL_CATEGORY_BANK
from backend.services.generator_helpers import make_question


def _build_localized_questions(item, question_bank, error_message):
    if len(question_bank) != 6:
        raise ValueError(error_message)

    prepared = []
    for index, question in enumerate(question_bank, start=1):
        points = int(question.get("points") or 200)
        answer = str(question.get("answer") or "").strip()
        text = str(question.get("question") or "").strip()
        options = [
            str(option or "").strip()
            for option in (question.get("options") or [])
            if str(option or "").strip()
        ]
        if not answer or not text:
            continue

        if answer not in options:
            options.insert(0, answer)

        cleaned_options = []
        for option in options:
            if option not in cleaned_options:
                cleaned_options.append(option)

        difficulty = "easy" if points == 200 else "medium" if points == 400 else "hard"
        prepared.append(
            make_question(
                f"{item['subcategoryId']}-{difficulty}-{index}",
                points,
                difficulty,
                text,
                answer,
                cleaned_options[:4],
            )
        )

    if len(prepared) != 6:
        raise ValueError(error_message.replace("is incomplete", "generator did not prepare 6 questions"))
    return prepared


def build_localized_general_questions(item, _cache):
    bank = GENERAL_CATEGORY_BANK.get(item.get("subcategoryId")) or []
    return _build_localized_questions(item, bank, "General Arabic bank is incomplete for this subcategory")


def build_localized_country_questions(item, _cache):
    bank = COUNTRY_CATEGORY_BANK.get(item.get("subcategoryId")) or []
    return _build_localized_questions(item, bank, "Country Arabic bank is incomplete for this subcategory")
