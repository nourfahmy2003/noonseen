"""Purpose: route all English→Arabic quiz wording through LibreTranslate with strict validation (live-only)."""

from backend.api_adapters.libretranslate import libretranslate_text
from backend.arabic.transform import (
    is_acceptable_arabic_brand_answer,
    is_acceptable_arabic_quiz_pair,
    normalize_arabic_text,
)
from backend.config import TRANSLATION_PROVIDER
from backend.utilities.debug import debug_log


def _require_libretranslate_provider():
    if TRANSLATION_PROVIDER != "libretranslate":
        raise ValueError(
            f'Unsupported TRANSLATION_PROVIDER "{TRANSLATION_PROVIDER}". '
            "Only libretranslate is supported for general quiz translation."
        )


def translate_quiz_pair(*, question_en: str, answer_en: str) -> tuple[str, str]:
    """Translate question+answer; returns Arabic strings or raises (no local heuristic fallback).
    
    Process:
    1. Fetch source question and answer in English
    2. Translate both via LibreTranslate
    3. Normalize Arabic text
    4. Validate that the Arabic is understandable and natural
    5. Discard and fail if translation is poor (no local fallback)
    """
    _require_libretranslate_provider()
    raw_q = str(question_en or "").strip()
    raw_a = str(answer_en or "").strip()
    if not raw_q or not raw_a:
        raise ValueError("translate_quiz_pair requires non-empty English question and answer.")

    debug_log("TRANSLATION", "Raw source question (English)", {"preview": raw_q[:240]})
    debug_log("TRANSLATION", "Raw source answer (English)", {"preview": raw_a[:120]})
    
    try:
        question_ar = normalize_arabic_text(libretranslate_text(text=raw_q, source_lang="en", target_lang="ar"))
    except Exception as error:
        debug_log("REJECTED", "Question translation failed via LibreTranslate", {"error": str(error)})
        raise ValueError(f"Question translation failed: {error}")
        
    try:
        answer_ar = normalize_arabic_text(libretranslate_text(text=raw_a, source_lang="en", target_lang="ar"))
    except Exception as error:
        debug_log("REJECTED", "Answer translation failed via LibreTranslate", {"error": str(error)})
        raise ValueError(f"Answer translation failed: {error}")

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
            "Arabic validation failed after LibreTranslate",
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
    """Purpose: turn a live company name into short natural Arabic for logo reveal answers.
    
    Process:
    1. Take the company name from API
    2. Send to LibreTranslate with a hint that it's a brand/company name
    3. Normalize the Arabic
    4. Validate that the output is natural and brief
    5. Fail clearly if translation is poor (no local fallback)
    """
    _require_libretranslate_provider()
    raw = str(company_name_en or "").strip()
    if not raw:
        raise ValueError("translate_brand_answer_ar requires a company name.")
    
    debug_log("TRANSLATION", "Brand name (English)", {"brand_name": raw})
    
    # Add context to LibreTranslate to get better brand name translations.
    prompt = f"{raw} (brand or company name, translate to Arabic only, no explanation or extra text)"
    try:
        answer_ar = normalize_arabic_text(libretranslate_text(text=prompt, source_lang="en", target_lang="ar"))
    except Exception as error:
        debug_log("REJECTED", "Brand translation failed via LibreTranslate", {"error": str(error), "brand": raw})
        raise ValueError(f"Brand translation failed: {error}")
    
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
