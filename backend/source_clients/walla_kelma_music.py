"""Purpose: fetch live music acting targets for Walla Kelma from TheAudioDB."""

from backend.config import AUDIO_DB_API_BASE, AUDIO_DB_API_KEY
from backend.services.repeat_prevention import choose_records
from backend.utilities.debug import debug_log
from backend.utilities.http import fetch_json
from backend.utilities.ids import source_record_id


def fetch_prompt(category, difficulty):
    format_name = "track" if difficulty != "easy" else "album"
    debug_log(
        "API REQUEST",
        "Calling API",
        {"url": f"{AUDIO_DB_API_BASE}/{AUDIO_DB_API_KEY}/mostloved.php", "params": {"format": format_name}},
    )
    payload = fetch_json(f"{AUDIO_DB_API_BASE}/{AUDIO_DB_API_KEY}/mostloved.php", query={"format": format_name})
    key = "loved" if isinstance(payload, dict) else None
    records = payload.get(key) or payload.get("mostloved") or []
    debug_log("API RESPONSE", "Raw response received", records[:3] if isinstance(records, list) else records)
    records = [
        item
        for item in records
        if isinstance(item, dict)
        and str(item.get("strTrack") or item.get("strAlbum") or item.get("strArtist") or "").strip()
    ]
    picked = choose_records(
        f"walla:{category}:{difficulty}",
        records,
        1,
        lambda item: source_record_id("audiodb", item.get("idTrack") or item.get("idAlbum") or item.get("idArtist")),
    )[0]
    debug_log("WALLA", "Source record", picked)
    secret = str(picked.get("strTrack") or picked.get("strAlbum") or picked.get("strArtist") or "").strip()
    debug_log("WALLA", "Secret generated", secret)
    return {
        "id": source_record_id("audiodb", picked.get("idTrack") or picked.get("idAlbum") or picked.get("idArtist")),
        "difficulty": difficulty,
        "secret_value": secret,
        "secret_value_ar": secret,
        "display_hint_ar": "مثّل اسمًا موسيقيًا دون قول العنوان أو تهجئته.",
        "metadata": {"artist": picked.get("strArtist"), "music_type": format_name},
    }
