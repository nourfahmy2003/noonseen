"""Purpose: English→Arabic via Lingva (Google Translate front-end) when LibreTranslate is unavailable.

Uses GET /api/v1/{source}/{target}/{urlencoded_text}. Requires a browser-like User-Agent on lingva.ml.
"""

import json
import random
import threading
import time
import urllib.parse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from backend.config import LINGVA_BASE_URL
from backend.utilities.debug import debug_log


# Lingva and similar proxies often block non-browser user agents.
_DEFAULT_UA = "Mozilla/5.0 (compatible; NoonJeem/1.0; +https://github.com/nourfahmy2003/noonjeem)"
_MAX_URL_CHARS = 5500

# Public Lingva instances rate-limit hard on concurrent requests; serialize globally.
_LINGVA_REQUEST_LOCK = threading.Lock()


def lingva_translate_text(*, text: str, source_lang: str = "en", target_lang: str = "ar") -> str:
    """Translate plain text; raises ValueError on failure."""
    raw = str(text or "")
    if not raw.strip():
        raise ValueError("lingva_translate_text requires non-empty text.")

    source = (source_lang or "en").lower().split("-")[0]
    target = (target_lang or "ar").lower().split("-")[0]
    base = (LINGVA_BASE_URL or "https://lingva.ml").strip().rstrip("/")
    encoded = urllib.parse.quote(raw, safe="")
    url = f"{base}/api/v1/{source}/{target}/{encoded}"
    if len(url) > _MAX_URL_CHARS:
        raise ValueError(
            f"Text is too long for Lingva URL transport ({len(url)} chars). "
            "Use LibreTranslate (POST) with LIBRETRANSLATE_BASE_URL instead."
        )

    debug_log(
        "TRANSLATION",
        "Lingva request",
        {"base": base, "source": source, "target": target, "q_chars": len(raw), "url_chars": len(url)},
    )

    parsed = None
    with _LINGVA_REQUEST_LOCK:
        for attempt in range(1, 7):
            request = Request(url, headers={"User-Agent": _DEFAULT_UA}, method="GET")
            try:
                with urlopen(request, timeout=35) as response:
                    parsed = json.loads(response.read().decode("utf-8"))
                time.sleep(0.28 + random.uniform(0.02, 0.12))
                break
            except HTTPError as error:
                if error.code in (429, 503) and attempt < 6:
                    delay = (1.1 * attempt) + random.uniform(0.2, 0.9)
                    debug_log(
                        "TRANSLATION",
                        "Lingva rate-limited or busy; retrying",
                        {"attempt": attempt, "code": error.code, "sleep_s": round(delay, 2)},
                    )
                    time.sleep(delay)
                    continue
                raise ValueError(f"Lingva HTTP {error.code}") from error
            except URLError as error:
                if attempt < 6:
                    time.sleep(0.6 * attempt)
                    continue
                raise ValueError(f"Lingva unreachable: {error}") from error
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise ValueError(f"Lingva bad response: {error}") from error

        if parsed is None:
            raise ValueError("Lingva failed after retries.")

    if isinstance(parsed, dict) and parsed.get("error"):
        raise ValueError(f"Lingva API error: {parsed.get('error')}")

    translated = parsed.get("translation") if isinstance(parsed, dict) else None
    if not isinstance(translated, str) or not translated.strip():
        debug_log("TRANSLATION", "Lingva rejected: bad response shape", {"keys": list(parsed.keys()) if isinstance(parsed, dict) else type(parsed).__name__})
        raise ValueError("Lingva returned an empty or invalid translation field.")

    out = translated.strip()
    debug_log("TRANSLATION", "Lingva response summary", {"out_chars": len(out), "preview": out[:120]})
    return out
