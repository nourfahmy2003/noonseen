"""Purpose: declare the live-only source mappings used by runtime quiz preparation.

Routing reminders (see `backend/source_clients/the_trivia.py`):
- `معلومات عامة` → The Trivia API v2 + LibreTranslate.
- `تاريخ` / `تكنولوجيا` / `عالم الحيوان` → Open Trivia DB + LibreTranslate (same client module key `the_trivia`).
- `شعارات وعلامات تجارية` → API Ninjas Logo API + LibreTranslate for Arabic brand labels.
"""

from backend.api_adapters.islamic_quiz_api import is_islamic_quiz_api_available
from backend.config import (
    API_FOOTBALL_API_KEY,
    API_NINJAS_API_KEY,
    KALIMALAB_API_TOKEN,
    TMDB_BEARER_TOKEN,
)
from backend.models.schemas import SourceDefinition
from backend.utilities.debug import debug_log


ACTIVE_ISLAMIC_CATEGORIES = (
    "التفسير",
    "العقيدة",
    "الحديث",
    "الفقه",
    "التاريخ",
    "اللغة العربية",
)


SOURCE_REGISTRY: dict[str, SourceDefinition] = {
    "لغة وأدب": {"backend_category": "لغة وأدب", "client_key": "kalimalab", "source": "KalimaLab", "source_type": "api", "requires_auth": True, "mode": "quiz"},
    "حروف": {"backend_category": "حروف", "client_key": "kalimalab", "source": "KalimaLab", "source_type": "api", "requires_auth": True, "mode": "quiz"},
    "حروف متحركة": {"backend_category": "حروف متحركة", "client_key": "kalimalab", "source": "KalimaLab", "source_type": "api", "requires_auth": True, "mode": "quiz"},
    "حروف إسلامي": {"backend_category": "حروف إسلامي", "client_key": "alquran_cloud", "source": "AlQuran Cloud", "source_type": "api", "requires_auth": False, "mode": "quiz", "pool": "quran"},
    "تاريخ": {"backend_category": "تاريخ", "client_key": "the_trivia", "source": "The Trivia API", "source_type": "api", "requires_auth": False, "mode": "quiz"},
    "معلومات عامة": {"backend_category": "معلومات عامة", "client_key": "the_trivia", "source": "The Trivia API", "source_type": "api", "requires_auth": False, "mode": "quiz"},
    "تكنولوجيا": {"backend_category": "تكنولوجيا", "client_key": "the_trivia", "source": "The Trivia API", "source_type": "api", "requires_auth": False, "mode": "quiz"},
    "عالم الحيوان": {"backend_category": "عالم الحيوان", "client_key": "the_trivia", "source": "The Trivia API", "source_type": "api", "requires_auth": False, "mode": "quiz"},
    "شعارات وعلامات تجارية": {"backend_category": "شعارات وعلامات تجارية", "client_key": "api_ninjas_logo", "source": "API Ninjas Logo API", "source_type": "api", "requires_auth": True, "mode": "quiz"},
    "جغرافيا": {"backend_category": "جغرافيا", "client_key": "rest_countries", "source": "REST Countries", "source_type": "api", "requires_auth": False, "mode": "quiz"},
    "دول وعواصم": {"backend_category": "دول وعواصم", "client_key": "rest_countries", "source": "REST Countries", "source_type": "api", "requires_auth": False, "mode": "quiz"},
    # Keep the spaced Arabic label as an alias because older UI selections and
    # cached payloads may still send it.
    "دول و عواصم": {"backend_category": "دول وعواصم", "client_key": "rest_countries", "source": "REST Countries", "source_type": "api", "requires_auth": False, "mode": "quiz"},
    "أعلام": {"backend_category": "أعلام", "client_key": "rest_countries", "source": "REST Countries", "source_type": "api", "requires_auth": False, "mode": "quiz"},
    "ما هي الدولة": {"backend_category": "ما هي الدولة", "client_key": "rest_countries", "source": "REST Countries", "source_type": "api", "requires_auth": False, "mode": "quiz"},
    "سياحة وسفر": {"backend_category": "سياحة وسفر", "client_key": "rest_countries", "source": "REST Countries", "source_type": "api", "requires_auth": False, "mode": "quiz"},
    "عملات": {"backend_category": "عملات", "client_key": "rest_countries", "source": "REST Countries", "source_type": "api", "requires_auth": False, "mode": "quiz"},
    "التفسير": {"backend_category": "التفسير", "client_key": "islamic_quiz_api", "source": "IslamicQuizAPI", "source_type": "api", "requires_auth": False, "mode": "quiz"},
    "العقيدة": {"backend_category": "العقيدة", "client_key": "islamic_quiz_api", "source": "IslamicQuizAPI", "source_type": "api", "requires_auth": False, "mode": "quiz"},
    "الحديث": {"backend_category": "الحديث", "client_key": "islamic_quiz_api", "source": "IslamicQuizAPI", "source_type": "api", "requires_auth": False, "mode": "quiz"},
    "الفقه": {"backend_category": "الفقه", "client_key": "islamic_quiz_api", "source": "IslamicQuizAPI", "source_type": "api", "requires_auth": False, "mode": "quiz"},
    "التاريخ": {"backend_category": "التاريخ", "client_key": "islamic_quiz_api", "source": "IslamicQuizAPI", "source_type": "api", "requires_auth": False, "mode": "quiz"},
    "اللغة العربية": {"backend_category": "اللغة العربية", "client_key": "islamic_quiz_api", "source": "IslamicQuizAPI", "source_type": "api", "requires_auth": False, "mode": "quiz"},
}

WALLA_KELMA_SOURCE_REGISTRY: dict[str, SourceDefinition] = {
    "ولا كلمة": {"backend_category": "ولا كلمة", "client_key": "walla_kelma_arabic", "source": "ولا كلمة عربي", "source_type": "curated", "requires_auth": False, "mode": "walla_kelma"},
    "ولا كلمة عامة": {"backend_category": "ولا كلمة عامة", "client_key": "walla_kelma_arabic", "source": "ولا كلمة عربي", "source_type": "curated", "requires_auth": False, "mode": "walla_kelma"},
    "ولا كلمة من أجنبي": {"backend_category": "ولا كلمة من أجنبي", "client_key": "walla_kelma_tmdb", "source": "TMDB", "source_type": "api", "requires_auth": True, "mode": "walla_kelma"},
    "ولا كلمة كروية": {"backend_category": "ولا كلمة كروية", "client_key": "walla_kelma_football", "source": "API-Football", "source_type": "api", "requires_auth": True, "mode": "walla_kelma"},
    "ولا كلمة إسلامي": {"backend_category": "ولا كلمة إسلامي", "client_key": "walla_kelma_islamic", "source": "IslamicQuizAPI", "source_type": "api", "requires_auth": False, "mode": "walla_kelma"},
    "Walla Kelma English General": {"backend_category": "ولا كلمة عامة", "client_key": "walla_kelma_arabic", "source": "ولا كلمة عربي", "source_type": "curated", "requires_auth": False, "mode": "walla_kelma"},
    "Walla Kelma English Movies": {"backend_category": "ولا كلمة", "client_key": "walla_kelma_arabic", "source": "ولا كلمة عربي", "source_type": "curated", "requires_auth": False, "mode": "walla_kelma"},
    "Walla Kelma English Series": {"backend_category": "ولا كلمة", "client_key": "walla_kelma_arabic", "source": "ولا كلمة عربي", "source_type": "curated", "requires_auth": False, "mode": "walla_kelma"},
    "Walla Kelma English Music": {"backend_category": "ولا كلمة", "client_key": "walla_kelma_arabic", "source": "ولا كلمة عربي", "source_type": "curated", "requires_auth": False, "mode": "walla_kelma"},
    "Walla Kelma English Football": {"backend_category": "ولا كلمة كروية", "client_key": "walla_kelma_football", "source": "API-Football", "source_type": "api", "requires_auth": True, "mode": "walla_kelma"},
}


def get_source_definition(category):
    definition = SOURCE_REGISTRY.get(category)
    if category in ACTIVE_ISLAMIC_CATEGORIES:
        debug_log("CATEGORY", "Active Islamic categories", ACTIVE_ISLAMIC_CATEGORIES)
    debug_log(
        "SOURCE",
        f'Category "{category}" → using {definition["client_key"] if definition else "None"}',
        definition,
    )
    return definition


def has_live_source_definition(category):
    definition = get_source_definition(category)
    if not definition:
        debug_log("SOURCE", f'Category "{category}" has no live source definition', None)
        return False
    if definition["client_key"] == "kalimalab":
        is_live = bool(KALIMALAB_API_TOKEN)
        debug_log("SOURCE", f'Category "{category}" live availability', {"available": is_live})
        return is_live
    if definition["client_key"] == "islamic_quiz_api":
        is_live = is_islamic_quiz_api_available(required_categories=[category])
        debug_log("SOURCE", f'Category "{category}" live availability', {"available": is_live})
        return is_live
    if definition["client_key"] == "api_ninjas_logo":
        is_live = bool(API_NINJAS_API_KEY)
        debug_log(
            "SOURCE",
            f'Category "{category}" live availability',
            {"available": is_live, "has_api_ninjas_key": is_live},
        )
        return is_live
    debug_log("SOURCE", f'Category "{category}" live availability', {"available": True})
    return True


def get_walla_kelma_source_definition(category):
    definition = WALLA_KELMA_SOURCE_REGISTRY.get(category)
    debug_log(
        "SOURCE",
        f'Category "{category}" → using {definition["client_key"] if definition else "None"}',
        definition,
    )
    return definition


def has_walla_kelma_live_source_definition(category):
    definition = get_walla_kelma_source_definition(category)
    if not definition:
        debug_log("SOURCE", f'Category "{category}" has no Walla Kelma live source definition', None)
        return False
    if definition["client_key"] == "walla_kelma_tmdb":
        is_live = bool(TMDB_BEARER_TOKEN)
        debug_log("SOURCE", f'Category "{category}" Walla Kelma live availability', {"available": is_live})
        return is_live
    if definition["client_key"] == "walla_kelma_football":
        is_live = bool(API_FOOTBALL_API_KEY)
        debug_log("SOURCE", f'Category "{category}" Walla Kelma live availability', {"available": is_live})
        return is_live
    if definition["client_key"] == "walla_kelma_islamic":
        is_live = is_islamic_quiz_api_available()
        debug_log("SOURCE", f'Category "{category}" Walla Kelma live availability', {"available": is_live})
        return is_live
    debug_log("SOURCE", f'Category "{category}" Walla Kelma live availability', {"available": True})
    return True
