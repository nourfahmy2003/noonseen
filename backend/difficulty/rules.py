"""Purpose: keep board difficulty sequencing and source difficulty normalization deterministic."""

import re
from typing import Optional


DIFFICULTY_SLOTS = (
    ("easy", 200),
    ("easy", 200),
    ("medium", 400),
    ("medium", 400),
    ("hard", 600),
    ("hard", 600),
)

LOGO_EASY_NAMES = {
    "adidas",
    "amazon",
    "apple",
    "bmw",
    "coca cola",
    "coca-cola",
    "disney",
    "google",
    "instagram",
    "intel",
    "mcdonalds",
    "mcdonald's",
    "mercedes benz",
    "mercedes-benz",
    "microsoft",
    "netflix",
    "nike",
    "pepsi",
    "playstation",
    "samsung",
    "sony",
    "starbucks",
    "tesla",
    "tiktok",
    "toyota",
    "visa",
    "youtube",
}

LOGO_MEDIUM_NAMES = {
    "airbnb",
    "canon",
    "dell",
    "ebay",
    "fedex",
    "hp",
    "huawei",
    "ikea",
    "kia",
    "lego",
    "lenovo",
    "mastercard",
    "oracle",
    "paypal",
    "puma",
    "shell",
    "slack",
    "snapchat",
    "spotify",
    "uber",
    "xerox",
    "zara",
    "adobe",
    "cisco",
    "nvidia",
    "linkedin",
    "shopify",
    "zoom",
    "dropbox",
    "panasonic",
    "nikon",
    "moderna",
    "pfizer",
    "jpmorgan",
    "goldman sachs",
    "barclays",
    "siemens",
    "3m",
    "caterpillar",
    "john deere",
    "dhl",
    "ups",
    "nestle",
    "unilever",
    "xiaomi",
    "nintendo",
    "playstation",
    "xbox",
}


def iter_difficulty_slots():
    return list(DIFFICULTY_SLOTS)


def normalize_difficulty(value, default="medium"):
    normalized = str(value or "").strip().lower()
    if normalized in {"easy", "medium", "hard"}:
        return normalized
    if normalized in {"simple", "beginner"}:
        return "easy"
    if normalized in {"difficult", "expert"}:
        return "hard"
    return default


def score_general_record(category, question_text, answer_text, source_difficulty=None):
    # The live APIs give partial difficulty signals, so this scorer nudges each
    # record toward the level that best matches the host-led Arabic reveal format.
    question = str(question_text or "").strip().lower()
    answer = str(answer_text or "").strip().lower()
    score = {"easy": 1, "medium": 2, "hard": 3}.get(normalize_difficulty(source_difficulty), 2)

    if len(question) > 95:
        score += 1
    if re.search(r"\b(when|year|which year|in what year|which company|which scientist|which animal)\b", question):
        score += 1
    if re.search(r"\b(first|largest|smallest|highest|oldest|capital|planet|country)\b", question):
        score -= 1
    if re.search(r"\b(protocol|browser|kernel|database|algorithm|species|habitat|dynasty|revolution|treaty)\b", question):
        score += 1
    if category == "تاريخ" and re.search(r"\b(empire|battle|revolution|treaty|century)\b", question):
        score += 1
    if category == "تكنولوجيا" and re.search(r"\b(protocol|software|hardware|operating system|browser|programming)\b", question):
        score += 1
    if category == "عالم الحيوان" and re.search(r"\b(species|predator|habitat|vertebrate|genus)\b", question):
        score += 1
    if len(answer.split()) > 3:
        score += 1

    if score <= 1:
        return "easy"
    if score >= 3:
        return "hard"
    return "medium"


def normalize_islamic_quiz_difficulty(value, question_text="", answer_text=""):
    """Map IslamicQuizAPI levels to board difficulty with deterministic text fallback."""
    normalized = str(value or "").strip().lower()
    if normalized in {"1", "easy"}:
        return "easy"
    if normalized in {"2", "medium"}:
        return "medium"
    if normalized in {"3", "hard"}:
        return "hard"

    question = str(question_text or "").strip()
    answer = str(answer_text or "").strip()
    complexity_score = 0

    # Longer prompts and answers usually correspond to narrower topic knowledge.
    if len(question) >= 70:
        complexity_score += 1
    if len(answer.split()) >= 5:
        complexity_score += 1
    if "قال" in question or "قوله تعالى" in question:
        complexity_score += 1

    if complexity_score <= 0:
        return "easy"
    if complexity_score >= 2:
        return "hard"
    return "medium"


def _logo_substring_bucket(normalized_name: str) -> Optional[str]:
    """Purpose: match noisy API company strings against curated famous brand substrings."""
    for brand in sorted(LOGO_EASY_NAMES, key=len, reverse=True):
        if brand in normalized_name:
            return "easy"
    for brand in sorted(LOGO_MEDIUM_NAMES, key=len, reverse=True):
        if brand in normalized_name:
            return "medium"
    return None


def score_logo_record(company_name, ticker="", image_url=""):
    """Purpose: map each live logo row into easy/medium/hard without starving any Jeopardy slot."""
    normalized_name = re.sub(r"[^a-z0-9]+", " ", str(company_name or "").strip().lower()).strip()
    normalized_ticker = str(ticker or "").strip().upper()
    normalized_image = str(image_url or "").strip().lower()

    substring_bucket = _logo_substring_bucket(normalized_name)
    if substring_bucket == "easy":
        return "easy"
    if substring_bucket == "medium":
        return "medium"
    if normalized_name in LOGO_EASY_NAMES:
        return "easy"
    if normalized_name in LOGO_MEDIUM_NAMES:
        return "medium"
    if normalized_ticker and len(normalized_ticker) <= 4 and normalized_name.count(" ") <= 1:
        return "medium"
    if any(keyword in normalized_image for keyword in ("apple", "google", "nike", "tesla", "amazon")):
        return "easy"
    # Longer multi-word corporate strings skew niche → hard; short unknown tokens stay medium.
    if len(normalized_name) >= 26 or normalized_name.count(" ") >= 3:
        return "hard"
    if len(normalized_name) <= 10 and normalized_name.count(" ") == 0:
        return "medium"
    return "hard"
