"""Purpose: create private live Walla Kelma sessions and serialize safe/public payloads."""

from urllib.parse import urlencode

from backend.models.schemas import WallaKelmaPrompt
from backend.services.category_mapping import get_unavailable_reason, map_walla_kelma_category
from backend.services.walla_kelma_session import complete_session, create_session, get_session
from backend.source_clients.walla_kelma_datamuse import fetch_prompt as fetch_datamuse_prompt
from backend.source_clients.walla_kelma_football import fetch_prompt as fetch_football_prompt
from backend.source_clients.walla_kelma_islamic import fetch_prompt as fetch_islamic_prompt
from backend.source_clients.walla_kelma_music import fetch_prompt as fetch_music_prompt
from backend.source_clients.walla_kelma_arabic import fetch_prompt as fetch_arabic_prompt
from backend.source_clients.walla_kelma_tmdb import fetch_prompt as fetch_tmdb_prompt
from backend.source_registry import (
    get_walla_kelma_source_definition,
    has_walla_kelma_live_source_definition,
)
from backend.utilities.debug import debug_log, debug_preview


WALLA_KELMA_CLIENTS = {
    "walla_kelma_datamuse": fetch_datamuse_prompt,
    "walla_kelma_arabic": fetch_arabic_prompt,
    "walla_kelma_tmdb": fetch_tmdb_prompt,
    "walla_kelma_music": fetch_music_prompt,
    "walla_kelma_football": fetch_football_prompt,
    "walla_kelma_islamic": fetch_islamic_prompt,
}
VALID_DIFFICULTIES = {"easy", "medium", "hard"}


def _validate_prompt(prompt: WallaKelmaPrompt) -> WallaKelmaPrompt:
    required_fields = ("id", "difficulty", "secret_value", "source", "source_type", "category")
    for field in required_fields:
        if not str(prompt.get(field) or "").strip():
            debug_log("REJECTED", "Reason", f"Invalid Walla Kelma prompt: missing {field}")
            raise ValueError(f"Invalid Walla Kelma prompt: missing {field}")
    prompt["mode"] = "walla_kelma"
    prompt["is_private"] = True
    prompt["secret_value_ar"] = str(prompt.get("secret_value_ar") or prompt["secret_value"]).strip()
    prompt["display_hint_ar"] = str(prompt.get("display_hint_ar") or "مثّل السر دون نطقه.").strip()
    prompt["metadata"] = prompt.get("metadata") or {}
    debug_log("WALLA", "Validated prompt", debug_preview(prompt, limit=8))
    return prompt


def _public_payload(session, public_base_url=""):
    prompt = session["prompt"]
    normalized_base_url = str(public_base_url or "").rstrip("/")
    qr_query = {"token": session["token"]}
    if normalized_base_url:
        qr_query["base"] = normalized_base_url
    qr_path = f"/walla-kelma.html?{urlencode(qr_query)}"
    qr_url = f"{normalized_base_url}{qr_path}" if normalized_base_url else qr_path
    payload = {
        "token": session["token"],
        "category": prompt["category"],
        "difficulty": prompt["difficulty"],
        "status": session["status"],
        "api_base_url": normalized_base_url,
        "qr_path": qr_path,
        "qr_url": qr_url,
        "expires_at": session["expires_at"],
    }
    debug_log("WALLA", "QR base URL", normalized_base_url or "same-origin")
    debug_log("WALLA", "Generated QR URL", qr_url)
    debug_log("WALLA", "Public payload", payload)
    return payload


def _private_payload(session):
    prompt = session["prompt"]
    payload = {
        "token": session["token"],
        "category": prompt["category"],
        "difficulty": prompt["difficulty"],
        "secret_value": prompt["secret_value"],
        "secret_value_ar": prompt["secret_value_ar"],
        "display_hint_ar": prompt["display_hint_ar"],
        "source": prompt["source"],
        "source_type": prompt["source_type"],
        "metadata": prompt.get("metadata") or {},
        "expires_at": session["expires_at"],
    }
    debug_log("WALLA", "Private payload", payload)
    return payload


def create_walla_kelma_session(item, difficulty, public_base_url=""):
    if difficulty not in VALID_DIFFICULTIES:
        debug_log("REJECTED", "Reason", "Walla Kelma difficulty must be easy, medium, or hard.")
        raise ValueError("Walla Kelma difficulty must be easy, medium, or hard.")
    category = map_walla_kelma_category(item)
    debug_log("CATEGORY", "Mapped backend categories", {"item": item, "backend_category": category})
    if category == "needs_label_confirmation":
        debug_log("REJECTED", "Reason", get_unavailable_reason(category))
        raise ValueError(get_unavailable_reason(category))
    if not has_walla_kelma_live_source_definition(category):
        debug_log("REJECTED", "Reason", get_unavailable_reason(category))
        raise ValueError(get_unavailable_reason(category))
    source_definition = get_walla_kelma_source_definition(category)
    debug_log(
        "SOURCE",
        f'Category "{category}" → using {source_definition["client_key"]}',
        source_definition,
    )
    try:
        prompt = WALLA_KELMA_CLIENTS[source_definition["client_key"]](category, difficulty)
    except Exception as error:
        debug_log("API ERROR", "Request failed", f"Live source failed for {category}: {error}")
        raise ValueError(
            f"Live source failed for {category}: {error}"
        ) from error
    prompt = _validate_prompt(
        {
            **prompt,
            "category": category,
            "source": source_definition["source"],
            "source_type": source_definition["source_type"],
        }
    )
    session = create_session(prompt)
    debug_log("WALLA", "Session created", {"token": session["token"], "category": category, "difficulty": difficulty})
    return _public_payload(session, public_base_url)


def get_walla_kelma_private_session(token):
    debug_log("WALLA", "Fetching private session", {"token": token})
    payload = _private_payload(get_session(token))
    debug_log("WALLA", "Token lookup success", {"token": token, "category": payload["category"]})
    return payload


def complete_walla_kelma(token, public_base_url=""):
    debug_log("WALLA", "Completing session", {"token": token})
    return _public_payload(complete_session(token), public_base_url)
