"""Purpose: English→Arabic for quiz and brands: LibreTranslate (POST) and/or Lingva (GET), with strict Arabic validation."""

from backend.api_adapters.libretranslate import libretranslate_text
from backend.api_adapters.lingva_translate import lingva_translate_text
from backend.arabic.transform import (
    is_acceptable_arabic_brand_answer,
    is_acceptable_arabic_quiz_pair,
    normalize_arabic_text,
)
from backend.config import LIBRETRANSLATE_BASE_URL, TRANSLATION_PROVIDER
from backend.utilities.debug import debug_log


def _translate_en_to_ar_line(*, text: str, source_lang: str = "en", target_lang: str = "ar") -> str:
    """Route one English string to Arabic using TRANSLATION_PROVIDER.

    hybrid (default): LibreTranslate when LIBRETRANSLATE_BASE_URL is set; on failure (rate limits, etc.) use Lingva.
    If the base URL is empty, use Lingva only.

    libretranslate: LibreTranslate only (raises if URL missing or API errors).

    lingva: Lingva only.
    """
    mode = TRANSLATION_PROVIDER
    if mode == "lingva":
        return lingva_translate_text(text=text, source_lang=source_lang, target_lang=target_lang)

    if mode == "libretranslate":
        return libretranslate_text(text=text, source_lang=source_lang, target_lang=target_lang)

    if not LIBRETRANSLATE_BASE_URL:
        debug_log("TRANSLATION", "Hybrid mode: no LibreTranslate URL; using Lingva", {})
        return lingva_translate_text(text=text, source_lang=source_lang, target_lang=target_lang)

    try:
        return libretranslate_text(text=text, source_lang=source_lang, target_lang=target_lang)
    except ValueError as error:
        debug_log(
            "TRANSLATION",
            "LibreTranslate failed; falling back to Lingva",
            {"error": str(error)[:220]},
        )
        return lingva_translate_text(text=text, source_lang=source_lang, target_lang=target_lang)


def translate_quiz_pair(*, question_en: str, answer_en: str) -> tuple[str, str]:
    """Translate question+answer; returns Arabic strings or raises (no local heuristic fallback)."""
    raw_q = str(question_en or "").strip()
    raw_a = str(answer_en or "").strip()
    if not raw_q or not raw_a:
        raise ValueError("translate_quiz_pair requires non-empty English question and answer.")

    debug_log("TRANSLATION", "Raw source question (English)", {"preview": raw_q[:240]})
    debug_log("TRANSLATION", "Raw source answer (English)", {"preview": raw_a[:120]})

    try:
        question_ar = normalize_arabic_text(_translate_en_to_ar_line(text=raw_q, source_lang="en", target_lang="ar"))
    except Exception as error:
        debug_log("REJECTED", "Question translation failed", {"error": str(error)})
        raise ValueError(f"Question translation failed: {error}") from error

    try:
        answer_ar = normalize_arabic_text(_translate_en_to_ar_line(text=raw_a, source_lang="en", target_lang="ar"))
    except Exception as error:
        debug_log("REJECTED", "Answer translation failed", {"error": str(error)})
        raise ValueError(f"Answer translation failed: {error}") from error

    debug_log(
        "TRANSLATION",
        "Translated quiz text preview",
        {
            "question_ar_preview": question_ar[:240],
            "answer_ar_preview": answer_ar[:160],
            "question_char_count": len(question_ar),
            "answer_char_count": len(answer_ar),
        },
    )

    ok, reason = is_acceptable_arabic_quiz_pair(question_ar, answer_ar)
    if not ok:
        debug_log(
            "REJECTED",
            "Arabic validation failed after machine translation",
            {
                "reason": reason,
                "question_ar": question_ar[:200],
                "answer_ar": answer_ar[:150],
            },
        )
        raise ValueError(f"Arabic quiz text failed validation: {reason}")

    debug_log(
        "FINAL",
        "Quiz pair translation succeeded",
        {
            "source_question_en": raw_q[:160],
            "source_answer_en": raw_a[:120],
            "result_question_ar": question_ar[:160],
            "result_answer_ar": answer_ar[:120],
        },
    )
    return question_ar, answer_ar


def translate_brand_answer_ar(*, company_name_en: str) -> str:
    """Turn a live company name into short natural Arabic for logo reveal answers."""
    raw = str(company_name_en or "").strip()
    if not raw:
        raise ValueError("translate_brand_answer_ar requires a company name.")

    debug_log("TRANSLATION", "Brand name (English)", {"brand_name": raw})

    prompt = f"{raw} (brand or company name, translate to Arabic only, no explanation or extra text)"
    try:
        answer_ar = normalize_arabic_text(_translate_en_to_ar_line(text=prompt, source_lang="en", target_lang="ar"))
    except Exception as error:
        debug_log("REJECTED", "Brand translation failed", {"error": str(error), "brand": raw})
        raise ValueError(f"Brand translation failed: {error}") from error

    debug_log(
        "TRANSLATION",
        "Brand translation result",
        {"source_brand": raw, "result_ar": answer_ar[:120], "char_count": len(answer_ar)},
    )

    ok, reason = is_acceptable_arabic_brand_answer(answer_ar)
    if not ok:
        debug_log(
            "REJECTED",
            "Brand Arabic validation failed",
            {"reason": reason, "brand": raw, "result_ar": answer_ar[:120]},
        )
        raise ValueError(f"Brand Arabic translation failed validation: {reason}")

    debug_log(
        "FINAL",
        "Brand translation succeeded",
        {"source_brand": raw, "result_ar": answer_ar},
    )
    return answer_ar
