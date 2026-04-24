"""Purpose: generate letter-based quiz questions from the localized letter banks."""

import random

from backend.data.letter_bank import LETTERS_CATEGORY_BANK
from backend.services.generator_helpers import make_options, make_question
from backend.utilities.text import first_visible_letter


def build_letters_questions(item, _cache):
    bank = LETTERS_CATEGORY_BANK.get(item.get("subcategoryId")) or []
    if len(bank) < 6:
        raise ValueError("Letters bank is incomplete for this subcategory")

    selected_items = random.sample(bank, 6)
    prompt_by_points = {
        200: 'أي إجابة تبدأ بحرف "{letter}" وتناسب الوصف التالي: {clue}',
        400: 'ما الاسم الذي يبدأ بحرف "{letter}" في فرع "{title}" ويطابق الوصف التالي: {clue}',
        600: 'اختر الإجابة التي يبدأ اسمها بحرف "{letter}" ويشير إليها هذا الدليل: {clue}',
    }
    prepared = []

    points_sequence = [200, 200, 400, 400, 600, 600]
    for index, (entry, points) in enumerate(zip(selected_items, points_sequence), start=1):
        answer = str(entry.get("answer") or "").strip()
        clue = str(entry.get("clue") or "").strip()
        if not answer or not clue:
            continue

        letter = first_visible_letter(answer)
        distractor_pool = [
            str(option.get("answer") or "").strip()
            for option in bank
            if str(option.get("answer") or "").strip() and str(option.get("answer") or "").strip() != answer
        ]
        distractors = random.sample(distractor_pool, min(6, len(distractor_pool)))
        options, _ = make_options(answer, distractors)
        difficulty = "easy" if points == 200 else "medium" if points == 400 else "hard"
        text = prompt_by_points[points].format(
            letter=letter,
            clue=clue,
            title=item.get("subcategoryTitle") or item.get("subcategoryId"),
        )
        prepared.append(
            make_question(
                f"{item['subcategoryId']}-{difficulty}-{index}",
                points,
                difficulty,
                text,
                answer,
                options,
            )
        )

    if len(prepared) != 6:
        raise ValueError("Letters generator did not prepare 6 questions")

    return prepared
