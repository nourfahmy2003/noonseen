"""Purpose: map UI selections onto flat live backend categories and grouped children.

The Arabic labels here must stay aligned with `SOURCE_REGISTRY` keys because they are the
canonical backend category strings used when preparing live Jeopardy boards.
"""

from backend.models.schemas import FlatCategorySelection, SelectedSubcategory
from backend.source_registry import (
    has_live_source_definition,
    has_walla_kelma_live_source_definition,
)


BACKEND_CATEGORY_BY_UI_ID = {
    "letters-general": "حروف",
    "letters-moving": "حروف متحركة",
    "letters-islamic": "حروف إسلامي",
    "letters-singing": "حروف أغاني",
    "letters-football": "حروف كروية",
    "letters-anime": "حروف أنمي",
    "general-technology": "تكنولوجيا",
    "general-general-knowledge": "معلومات عامة",
    "general-history": "تاريخ",
    "general-global-logos": "شعارات وعلامات تجارية",
    "general-logos": "شعارات وعلامات تجارية",
    "general-poetry": "عالم الشعر",
    "general-language-literature": "لغة وأدب",
    "general-animals": "عالم الحيوان",
    "countries-geography": "جغرافيا",
    "countries-country-capitals": "دول وعواصم",
    "countries-capitals": "دول وعواصم",
    "countries-travel": "سياحة وسفر",
    "countries-aviation": "عالم الطيران",
    "countries-flags": "أعلام",
    "countries-what-country": "ما هي الدولة",
    "countries-languages": "لغات ولهجات",
    "countries-currencies": "عملات",
    "islamic-tafseer": "التفسير",
    "islamic-aqeedah": "العقيدة",
    "islamic-hadith": "الحديث",
    "islamic-fiqh": "الفقه",
    "islamic-history": "التاريخ",
    "islamic-arabic-language": "اللغة العربية",
}

WALLA_KELMA_CATEGORY_BY_UI_ID = {
    "no-word-general": "ولا كلمة عامة",
    "no-word-default": "ولا كلمة",
    "no-word-foreign": "ولا كلمة من أجنبي",
    "no-word-football": "ولا كلمة كروية",
    "no-word-proverbs": "ولا كلمة أمثال",
    "no-word-anime": "ولا كلمة أنمي",
    "no-word-wrestling": "ولا كلمة مصارعة",
    "no-word-islamic": "ولا كلمة إسلامي",
}

NEEDS_LABEL_CONFIRMATION_IDS = {
    "countries-old-flags",
    "countries-presidents",
    "countries-uk-batch",
    "countries-anthem",
    "countries-world-war",
    "countries-maps",
    "general-refrigerators",
    "general-products",
}

UNAVAILABLE_RUNTIME_CATEGORIES = {
    "حروف أغاني": "No live source is configured for حروف أغاني.",
    "عالم الشعر": "No live source is configured for عالم الشعر.",
    "حروف كروية": "No live source is configured for حروف كروية.",
    "حروف أنمي": "No live source is configured for حروف أنمي.",
    "عالم الطيران": "عالم الطيران تحت الإنشاء حاليًا ولا يوجد له مصدر حي معتمد.",
    "لغات ولهجات": "لغات ولهجات تحت الإنشاء حاليًا ولا يوجد له مصدر حي معتمد.",
    "شعارات وعلامات تجارية": "شعارات وعلامات تجارية تحتاج مصدر API Ninjas Logo حيًا ومفتاح API_NINJAS_API_KEY صالحًا.",
    "ولا كلمة أمثال": "No live source is configured for ولا كلمة أمثال.",
    "ولا كلمة أنمي": "No live source is configured for ولا كلمة أنمي.",
    "ولا كلمة مصارعة": "No live source is configured for ولا كلمة مصارعة.",
}

UI_GROUP_CHILDREN_BY_KEY = {
    "islamic": [
        "islamic-tafseer",
        "islamic-aqeedah",
        "islamic-hadith",
        "islamic-fiqh",
        "islamic-history",
        "islamic-arabic-language",
    ],
    "إسلامي": [
        "islamic-tafseer",
        "islamic-aqeedah",
        "islamic-hadith",
        "islamic-fiqh",
        "islamic-history",
        "islamic-arabic-language",
    ],
}

UI_GROUP_TITLE_BY_KEY = {
    "islamic": "إسلامي",
    "إسلامي": "إسلامي",
}

UI_SUBCATEGORY_TITLE_BY_ID = {
    ui_id: backend_category
    for ui_id, backend_category in BACKEND_CATEGORY_BY_UI_ID.items()
}


def map_selected_subcategory(item: SelectedSubcategory) -> FlatCategorySelection:
    ui_id = item.get("subcategoryId") or ""
    backend_category = (
        "needs_label_confirmation"
        if ui_id in NEEDS_LABEL_CONFIRMATION_IDS
        else BACKEND_CATEGORY_BY_UI_ID.get(ui_id, "needs_label_confirmation")
    )
    return {
        "ui_subcategory_id": ui_id,
        "ui_title_ar": item.get("subcategoryTitle") or backend_category,
        "backend_category": backend_category,
        "imageKey": item.get("imageKey"),
        "iconKey": item.get("iconKey"),
        "flagCode": item.get("flagCode"),
    }


def get_ui_group_children(group_key: str | None) -> list[str]:
    normalized = str(group_key or "").strip()
    return list(UI_GROUP_CHILDREN_BY_KEY.get(normalized) or [])


def expand_grouped_selected_items(selected_items: list[SelectedSubcategory]) -> list[SelectedSubcategory]:
    expanded = []
    seen_subcategory_ids = set()

    for item in selected_items:
        ui_subcategory_id = str(item.get("subcategoryId") or "").strip()
        if ui_subcategory_id:
            if ui_subcategory_id not in seen_subcategory_ids:
                seen_subcategory_ids.add(ui_subcategory_id)
                expanded.append(item)
            continue

        group_key = (
            item.get("category")
            or item.get("categoryId")
            or item.get("categoryTitle")
        )
        group_children = get_ui_group_children(group_key)
        if not group_children:
            expanded.append(item)
            continue

        category_id = str(item.get("categoryId") or group_key or "").strip() or "islamic"
        category_title = str(item.get("categoryTitle") or UI_GROUP_TITLE_BY_KEY.get(str(group_key or "").strip()) or "").strip() or "إسلامي"
        icon_key = item.get("iconKey") or "mosque"

        for child_id in group_children:
            if child_id in seen_subcategory_ids:
                continue
            seen_subcategory_ids.add(child_id)
            expanded.append(
                {
                    **item,
                    "categoryId": category_id,
                    "categoryTitle": category_title,
                    "subcategoryId": child_id,
                    "subcategoryTitle": UI_SUBCATEGORY_TITLE_BY_ID.get(child_id, child_id),
                    "iconKey": icon_key,
                }
            )

    return expanded


def list_api_ready_ui_subcategory_ids() -> list[str]:
    return sorted(
        ui_id
        for ui_id, backend_category in BACKEND_CATEGORY_BY_UI_ID.items()
        if has_live_source_definition(backend_category)
    )


def list_walla_kelma_ready_ui_subcategory_ids() -> list[str]:
    return sorted(
        ui_id
        for ui_id, backend_category in WALLA_KELMA_CATEGORY_BY_UI_ID.items()
        if has_walla_kelma_live_source_definition(backend_category)
    )


def list_live_ui_subcategory_ids() -> list[str]:
    return sorted(set(list_api_ready_ui_subcategory_ids() + list_walla_kelma_ready_ui_subcategory_ids()))


def map_walla_kelma_category(item: SelectedSubcategory) -> str:
    ui_id = str(item.get("subcategoryId") or "").strip()
    if ui_id in WALLA_KELMA_CATEGORY_BY_UI_ID:
        return WALLA_KELMA_CATEGORY_BY_UI_ID[ui_id]
    title = str(item.get("subcategoryTitle") or "").strip()
    for _, category in WALLA_KELMA_CATEGORY_BY_UI_ID.items():
        if title == category:
            return category
    if title == "Walla Kelma English General":
        return "ولا كلمة عامة"
    if title in {
        "Walla Kelma English Movies",
        "Walla Kelma English Series",
        "Walla Kelma English Music",
    }:
        return "ولا كلمة"
    if title == "Walla Kelma English Football":
        return "ولا كلمة كروية"
    if title == "ولا كلمة إسلامي":
        return title
    return "needs_label_confirmation"


def get_unavailable_reason(backend_category: str) -> str:
    if backend_category == "needs_label_confirmation":
        return "This card needs exact Arabic label confirmation before backend implementation."
    return UNAVAILABLE_RUNTIME_CATEGORIES.get(
        backend_category,
        f"No live source is configured for {backend_category}.",
    )
