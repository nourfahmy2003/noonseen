"""Purpose: adapt live country data into the normalized shape used by quiz services."""

import time

from backend.arabic.transform import ensure_arabic_label
from backend.config import API_COUNTRIES_API_BASE, REST_COUNTRIES_API_BASE
from backend.data.catalogs import CONTINENT_LABELS, REGION_LABELS, SUBREGION_LABELS, WEEKDAY_LABELS
from backend.models.schemas import NormalizedCountry
from backend.utilities.debug import debug_log, debug_preview
from backend.utilities.http import fetch_json
from backend.utilities.text import flag_code_to_emoji

COUNTRY_NAME_OVERRIDES = {
    "Republic of the Congo": "جمهورية الكونغو",
    "Democratic Republic of the Congo": "جمهورية الكونغو الديمقراطية",
    "Angola": "أنغولا",
    "Czechia": "التشيك",
    "Laos": "لاوس",
    "Hong Kong": "هونغ كونغ",
    "North Macedonia": "مقدونيا الشمالية",
    "South Korea": "كوريا الجنوبية",
    "North Korea": "كوريا الشمالية",
}

REST_COUNTRIES_TIMEOUT_SECONDS = 30
REST_COUNTRIES_RETRY_BACKOFF_SECONDS = (1.5, 3.0)
REST_COUNTRIES_RESPONSE_CACHE = {}
REST_COUNTRIES_CACHE_TTL_SECONDS = 1800
APICOUNTRIES_CACHE_KEY = ("apicountries", "all")


def normalize_country(raw_country) -> NormalizedCountry:
    debug_log("RAW RECORD", "Incoming data", raw_country)
    if raw_country.get("alpha2Code"):
        name_en = raw_country.get("name") or raw_country.get("alpha2Code", "")
        name_ar = COUNTRY_NAME_OVERRIDES.get(name_en)
        if not name_ar:
            name_ar, _ = ensure_arabic_label(name_en)
        currencies = raw_country.get("currencies") or []
        languages = raw_country.get("languages") or []
        normalized = {
            "name": name_ar or name_en,
            "common_name": name_en,
            "capital": raw_country.get("capital") or None,
            "currency_codes": [item.get("code", "") for item in currencies if item.get("code")],
            "currency_names": [item.get("name", "") for item in currencies if item.get("name")],
            "languages": [item.get("name", "") for item in languages if item.get("name")],
            "flag": flag_code_to_emoji(raw_country.get("alpha2Code", "")),
            "flag_svg": (raw_country.get("flags") or {}).get("svg")
            or (raw_country.get("flags") or {}).get("png", ""),
            "cca2": raw_country.get("alpha2Code", ""),
            "cca3": raw_country.get("alpha3Code", ""),
            "region": raw_country.get("region", ""),
            "subregion": raw_country.get("subregion", ""),
            "population": int(raw_country.get("population") or 0),
            "continents": [raw_country.get("region")] if raw_country.get("region") else [],
            "borders": raw_country.get("borders") or [],
            "timezones": raw_country.get("timezones") or [],
            "maps": {},
            "start_of_week": "",
            "car_side": "",
            "landlocked": False,
            "area": raw_country.get("area") or 0,
            "independent": None,
            "un_member": None,
        }
        debug_log("TRANSFORM", "Built question context", debug_preview(normalized, limit=8))
        return normalized

    translations = raw_country.get("translations", {})
    arabic_translation = translations.get("ara", {})
    common_name = raw_country.get("name", {}).get("common", "")
    currencies = raw_country.get("currencies", {}) or {}
    languages = raw_country.get("languages", {}) or {}
    capitals = raw_country.get("capital") or []
    continents = raw_country.get("continents") or []
    overridden_name = COUNTRY_NAME_OVERRIDES.get(common_name)

    normalized = {
        "name": overridden_name
        or arabic_translation.get("common")
        or common_name
        or raw_country.get("cca2", ""),
        "common_name": common_name,
        "capital": capitals[0] if capitals else None,
        "currency_codes": list(currencies.keys()),
        "currency_names": [item.get("name", code) for code, item in currencies.items()],
        "languages": list(languages.values()),
        "flag": raw_country.get("flag") or flag_code_to_emoji(raw_country.get("cca2", "")),
        "flag_svg": (raw_country.get("flags") or {}).get("svg")
        or (raw_country.get("flags") or {}).get("png", ""),
        "cca2": raw_country.get("cca2", ""),
        "cca3": raw_country.get("cca3", ""),
        "region": raw_country.get("region", ""),
        "subregion": raw_country.get("subregion", ""),
        "population": int(raw_country.get("population") or 0),
        "continents": continents,
        "borders": raw_country.get("borders") or [],
        "timezones": raw_country.get("timezones") or [],
        "maps": raw_country.get("maps") or {},
        "start_of_week": raw_country.get("startOfWeek", ""),
        "car_side": (raw_country.get("car") or {}).get("side", ""),
        "landlocked": bool(raw_country.get("landlocked")),
        "area": raw_country.get("area") or 0,
        "independent": raw_country.get("independent") if "independent" in raw_country else None,
        "un_member": raw_country.get("unMember") if "unMember" in raw_country else None,
    }
    debug_log("TRANSFORM", "Built question context", debug_preview(normalized, limit=8))
    return normalized


def translate_region(value):
    return REGION_LABELS.get(value, value or "غير محدد")


def translate_subregion(value):
    return SUBREGION_LABELS.get(value, value or "غير محدد")


def translate_continent(value):
    return CONTINENT_LABELS.get(value, value or "غير محدد")


def translate_weekday(value):
    return WEEKDAY_LABELS.get(value, value or "الاثنين")


def _get_cached_payload(cache_key):
    cached = REST_COUNTRIES_RESPONSE_CACHE.get(cache_key)
    if not cached:
        return None
    if cached["expires_at"] <= time.time():
        REST_COUNTRIES_RESPONSE_CACHE.pop(cache_key, None)
        return None
    debug_log("API REQUEST", "REST Countries cache hit", {"cache_key": cache_key})
    return cached["payload"]


def _fetch_rest_countries_all(fields):
    cache_key = ("restcountries", tuple(fields))
    cached_payload = _get_cached_payload(cache_key)
    if cached_payload is not None:
        return cached_payload

    payload = fetch_json(
        f"{REST_COUNTRIES_API_BASE}/all",
        query={"fields": ",".join(fields)},
        timeout=REST_COUNTRIES_TIMEOUT_SECONDS,
        max_attempts=1 + len(REST_COUNTRIES_RETRY_BACKOFF_SECONDS),
        retry_backoff_seconds=REST_COUNTRIES_RETRY_BACKOFF_SECONDS,
    )
    REST_COUNTRIES_RESPONSE_CACHE[cache_key] = {
        "payload": payload,
        "expires_at": time.time() + REST_COUNTRIES_CACHE_TTL_SECONDS,
    }
    return payload


def _fetch_apicountries_all():
    cached_payload = _get_cached_payload(APICOUNTRIES_CACHE_KEY)
    if cached_payload is not None:
        return cached_payload
    payload = fetch_json(
        f"{API_COUNTRIES_API_BASE}/countries",
        timeout=REST_COUNTRIES_TIMEOUT_SECONDS,
        max_attempts=1 + len(REST_COUNTRIES_RETRY_BACKOFF_SECONDS),
        retry_backoff_seconds=REST_COUNTRIES_RETRY_BACKOFF_SECONDS,
    )
    REST_COUNTRIES_RESPONSE_CACHE[APICOUNTRIES_CACHE_KEY] = {
        "payload": payload,
        "expires_at": time.time() + REST_COUNTRIES_CACHE_TTL_SECONDS,
    }
    return payload


def get_country_context(cache):
    if cache.get("countries") is not None:
        debug_log("API RESPONSE", "Using cached REST Countries context", {"count": len(cache["countries"])})
        return cache["countries"]

    primary_fields = [
        "name",
        "translations",
        "capital",
        "currencies",
        "languages",
        "flags",
        "cca2",
        "cca3",
        "region",
    ]
    secondary_fields = [
        "cca3",
        "subregion",
        "population",
        "continents",
        "borders",
        "car",
        "landlocked",
        "area",
        "timezones",
        "startOfWeek",
    ]
    debug_log(
        "API REQUEST",
        "Preparing REST Countries primary request",
        {"url": f"{REST_COUNTRIES_API_BASE}/all", "params": {"fields": ",".join(primary_fields)}},
    )
    try:
        primary_data = _fetch_rest_countries_all(primary_fields)
        debug_log(
            "API REQUEST",
            "Preparing REST Countries secondary request",
            {"url": f"{REST_COUNTRIES_API_BASE}/all", "params": {"fields": ",".join(secondary_fields)}},
        )
        secondary_data = _fetch_rest_countries_all(secondary_fields)
        secondary_by_code = {
            country.get("cca3"): country
            for country in secondary_data
            if isinstance(country, dict) and country.get("cca3")
        }
        raw_data = [
            {**country, **secondary_by_code.get(country.get("cca3"), {})}
            for country in primary_data
            if isinstance(country, dict)
        ]
    except Exception as error:
        debug_log("API ERROR", "REST Countries unavailable, switching to APICountries", str(error))
        raw_data = [country for country in (_fetch_apicountries_all() or []) if isinstance(country, dict)]

    countries = [normalize_country(country) for country in raw_data]
    countries = [
        country
        for country in countries
        if country["name"] and country["cca2"] and country["population"] > 0
    ]
    countries.sort(key=lambda item: item["population"], reverse=True)
    cache["countries"] = countries
    debug_log("FINAL", "REST Countries normalized context ready", debug_preview(countries, limit=3))
    return countries
