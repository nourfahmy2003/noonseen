"""Purpose: score and filter live trivia rows so easy slots stay famous while hard slots stay substantive."""

import re

from backend.difficulty.rules import normalize_difficulty


def _lower(value: str) -> str:
    return str(value or "").strip().lower()


def is_obvious_trivia_cliche(question_en: str, answer_en: str) -> bool:
    """Reject repetitive kid-level prompts and weak content that leak through APIs too often."""
    q, a = _lower(question_en), _lower(answer_en)
    if not q or not a:
        return True
    if "which of these" in q or "true or false" in q or "all of the above" in q:
        return True
    if re.search(r"\b2\+2\b", q) or re.search(r"\b1\+1\b", q):
        return True
    if re.search(r"\bwhat color is\b", q) and re.search(r"\b(blue|red|green|yellow)\b", a):
        return True
    if len(a.split()) <= 1 and a in {"yes", "no", "water", "air", "sun", "moon", "earth"}:
        return True
    # Reject ultra-obvious single-word facts for better quiz quality.
    if len(a.split()) == 1 and len(a) <= 4:
        return True
    # Reject prompts asking for colors, numbers, or basic baby-level facts.
    if re.search(r"\b(how many|how much|what number)\b", q) and len(a) <= 3:
        return True
    if re.search(r"\bwhat is (the )?name of\b", q) and len(a.split()) == 1:
        return True
    return False


def content_substance_score(category: str, question_en: str, answer_en: str) -> int:
    """Higher scores prefer deeper, more meaningful prompts. Used to rank rows before bucketing.
    This heavily favors substantive content over trivial facts."""
    q, a = _lower(question_en), _lower(answer_en)
    score = 0
    words = len(q.split())
    
    # Prefer longer, more complex questions (they're usually more interesting).
    if words >= 20:
        score += 5
    elif words >= 15:
        score += 4
    elif words >= 12:
        score += 3
    elif words >= 9:
        score += 2
    elif words >= 6:
        score += 1

    # Prefer longer, multi-part answers.
    if len(a) >= 32:
        score += 3
    elif len(a) >= 24:
        score += 2
    elif len(a) >= 18:
        score += 1

    # Category-specific keyword scoring for deeper content.
    if category == "تاريخ":
        if re.search(r"\b(empire|revolution|treaty|dynasty|rebellion|invasion|colony|republic|monarchy|civilization)\b", q):
            score += 5
        if re.search(r"\b(century|bce|bc|ad|reign|coronation|abdication|campaign|siege)\b", q):
            score += 3
        if re.search(r"\b(when|year|what year|in what year)\b", q):
            score += 2
            
    elif category == "تكنولوجيا":
        if re.search(
            r"\b(protocol|kernel|database|algorithm|compiler|encryption|cpu|gpu|neural|packet|linux|unix|http|dns|ip|cache|pipeline|virtualization)\b",
            q,
        ):
            score += 5
        if re.search(r"\b(software|hardware|browser|programming|server|client|cloud|chip|framework|api)\b", q):
            score += 2
        if re.search(r"\b(who|inventor|created|developed|discovered)\b", q):
            score += 1
            
    elif category == "عالم الحيوان":
        if re.search(r"\b(species|genus|habitat|predator|vertebrate|mammal|reptile|amphibian|migration|ecosystem)\b", q):
            score += 5
        if re.search(r"\b(evolution|extinct|subspecies|taxonomy|endangered|carnivore|herbivore)\b", q):
            score += 3
        if re.search(r"\b(how many|what is the|which animal)\b", q):
            score += 1
            
    elif category == "معلومات عامة":
        if re.search(r"\b(molecule|element|theorem|latitude|longitude|capital|population|continent|physicist|mathematician)\b", q):
            score += 2
        if re.search(r"\b(when|in what year|what year)\b", q):
            score += 1
            
    return score


def combined_bucket(category: str, question_en: str, answer_en: str, api_difficulty: str | None) -> str:
    """Map a translated-ready English row onto easy/medium/hard using API hint + substance score.
    
    Prioritizes substantive content: harder questions should have meaningful depth,
    while easy questions should be famous/accessible but not trivial."""
    base = normalize_difficulty(api_difficulty, default="medium")
    score = content_substance_score(category, question_en, answer_en)

    if category == "تاريخ":
        # For history: strong preference for substantive content.
        # Only very basic history goes to easy.
        if score >= 8:
            return "hard"
        if score >= 4:
            return "medium"
        return "easy" if base == "easy" and score <= 2 else "medium"

    if category == "تكنولوجيا":
        # Tech: prefer harder classifications for real tech topics.
        if score >= 7:
            return "hard"
        if score >= 3:
            return "medium"
        return "easy" if base == "easy" and score <= 1 else "medium"

    if category == "عالم الحيوان":
        # Animals: avoid baby-level content even in easy.
        if score >= 7:
            return "hard"
        if score >= 3:
            return "medium"
        return "easy" if base == "easy" and score <= 1 else "medium"

    # معلومات عامة — strongly prefer API medium/hard signals; only trivial content → easy.
    if base == "hard" or score >= 8:
        return "hard"
    if base == "medium" or score >= 4:
        return "medium"
    return "easy"


def should_keep_for_category(category: str, question_en: str, answer_en: str) -> bool:
    """Drop rows that are too thin for the themed category before translation spend."""
    if is_obvious_trivia_cliche(question_en, answer_en):
        return False
    q = _lower(question_en)
    if category == "تاريخ" and len(q.split()) < 4:
        return False
    if category == "تكنولوجيا" and len(q.split()) < 4:
        return False
    if category == "عالم الحيوان" and len(q.split()) < 4:
        return False
    return True
