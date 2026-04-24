"""Purpose: collect small text-cleaning and display helpers reused across services."""

from backend.data.catalogs import ICON_BY_KEY


def icon_from_item(item):
    icon_key = item.get("iconKey")
    return ICON_BY_KEY.get(icon_key, "✨")


def flag_code_to_emoji(flag_code):
    normalized = str(flag_code or "").strip().upper()
    if len(normalized) != 2 or not normalized.isalpha():
        return ""
    return "".join(chr(127397 + ord(char)) for char in normalized)


def first_visible_letter(value):
    for char in str(value or "").strip():
        if not char.isspace():
            return char
    return "؟"


def clean_placeholder_question_text(text):
    value = str(text or "").strip()
    if ":" in value:
        value = value.split(":", 1)[1].strip()

    value = value.replace("الإجابة التجريبية", "الإجابة")
    value = value.replace("لهذا الفرع", "").replace("  ", " ").strip()
    if value.endswith("؟"):
        return value
    return value or "ما الإجابة المناسبة؟"


def clean_placeholder_answer_text(text):
    return str(text or "").strip() or "إجابة غير متاحة"


def clean_placeholder_options(options, answer):
    cleaned = []
    for option in options or []:
        value = str(option or "").strip()
        if value and value not in cleaned:
            cleaned.append(value)

    if answer not in cleaned:
        cleaned.insert(0, answer)
    return cleaned or [answer]


def sanitize_fake_question(question):
    answer = clean_placeholder_answer_text(question.get("answer"))
    options = clean_placeholder_options(question.get("options"), answer)
    correct_index = question.get("correctIndex", 0)

    if not isinstance(correct_index, int) or correct_index < 0 or correct_index >= len(options):
        correct_index = 0

    if answer not in options:
        options.insert(0, answer)
        correct_index = 0

    return {
        **question,
        "question": clean_placeholder_question_text(question.get("question")),
        "answer": answer,
        "options": options,
        "correctIndex": correct_index,
    }
