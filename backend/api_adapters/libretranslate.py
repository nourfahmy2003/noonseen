"""Purpose: call a LibreTranslate-compatible /translate endpoint for English→Arabic quiz text."""

from backend.config import LIBRETRANSLATE_API_KEY, LIBRETRANSLATE_BASE_URL
from backend.utilities.debug import debug_log, debug_preview
from backend.utilities.http import fetch_json_post


def _translate_url():
    if not LIBRETRANSLATE_BASE_URL:
        return ""
    return f"{LIBRETRANSLATE_BASE_URL.rstrip('/')}/translate"


def libretranslate_text(*, text: str, source_lang: str = "en", target_lang: str = "ar") -> str:
    """Translate a single string; raises ValueError on transport/shape errors (no silent fallback)."""
    base = LIBRETRANSLATE_BASE_URL.strip().rstrip("/")
    if not base:
        raise ValueError("LIBRETRANSLATE_BASE_URL is not configured; Arabic translation cannot run.")

    url = f"{base}/translate"
    payload = {
        "q": str(text or ""),
        "source": source_lang or "en",
        "target": target_lang or "ar",
        "format": "text",
    }
    if LIBRETRANSLATE_API_KEY:
        payload["api_key"] = LIBRETRANSLATE_API_KEY

    debug_log(
        "TRANSLATION",
        "LibreTranslate request summary",
        {
            "url": url,
            "source": payload["source"],
            "target": payload["target"],
            "q_chars": len(payload["q"]),
            "has_api_key_field": bool(LIBRETRANSLATE_API_KEY),
        },
    )

    response = fetch_json_post(url, payload, max_attempts=2, retry_backoff_seconds=(0.75,), retry_on_statuses={429})
    if isinstance(response, dict) and response.get("error"):
        err = str(response.get("error") or "unknown error")
        debug_log("TRANSLATION", "LibreTranslate API error field", {"error": err[:200]})
        raise ValueError(
            f"LibreTranslate error: {err}. "
            "Often this is rate limiting; retry later. If the server asks for a key, set LIBRETRANSLATE_API_KEY "
            "(optional for many self-hosted instances). Hybrid mode will fall back to Lingva when caught upstream."
        )
    translated = response.get("translatedText") if isinstance(response, dict) else None
    if not isinstance(translated, str) or not translated.strip():
        debug_log("TRANSLATION", "LibreTranslate rejected: bad response shape", debug_preview(response, limit=2))
        raise ValueError("LibreTranslate returned an empty or invalid translatedText field.")

    debug_log(
        "TRANSLATION",
        "LibreTranslate response summary",
        {"out_chars": len(translated.strip()), "preview": translated.strip()[:120]},
    )
    return translated.strip()
