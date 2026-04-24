"""Purpose: serve Arabic-only Walla Kelma prompts for general and entertainment rounds."""

from backend.services.repeat_prevention import choose_records
from backend.utilities.debug import debug_log
from backend.utilities.ids import source_record_id


GENERAL_PROMPTS_BY_DIFFICULTY = {
    "easy": [
        {"value": "تفاحة", "hint": "مثّل شيئًا يؤكل ويكون شائعًا في الفواكه."},
        {"value": "سيارة", "hint": "مثّل وسيلة نقل يستخدمها الناس يوميًا."},
        {"value": "ساعة", "hint": "مثّل شيئًا نلبسه أو نحمله لمعرفة الوقت."},
        {"value": "مفتاح", "hint": "مثّل شيئًا صغيرًا نستخدمه لفتح الأبواب."},
        {"value": "مدرسة", "hint": "مثّل مكانًا يذهب إليه الطلاب يوميًا."},
        {"value": "هاتف", "hint": "مثّل جهازًا نتواصل به مع الآخرين."},
        {"value": "قهوة", "hint": "مثّل مشروبًا ساخنًا مشهورًا عند الكبار."},
        {"value": "مطر", "hint": "مثّل ظاهرة تنزل من السماء في الشتاء."},
        {"value": "ملعقة", "hint": "مثّل أداة نستخدمها في الأكل."},
        {"value": "كرة", "hint": "مثّل شيئًا دائريًا يُلعب به."},
        {"value": "مطار", "hint": "مثّل مكانًا تبدأ منه رحلات السفر الجوية."},
        {"value": "شمس", "hint": "مثّل شيئًا يظهر نهارًا ويعطي ضوءًا وحرارة."},
    ],
    "medium": [
        {"value": "مكتبة", "hint": "مثّل مكانًا يرتبط بالكتب والقراءة والهدوء."},
        {"value": "حديقة", "hint": "مثّل مكانًا مفتوحًا يذهب إليه الناس للتنزه."},
        {"value": "قطار", "hint": "مثّل وسيلة نقل تسير على سكة طويلة."},
        {"value": "عطلة", "hint": "مثّل فترة ينتظرها الناس للراحة والسفر."},
        {"value": "مرآة", "hint": "مثّل شيئًا ننظر إليه لرؤية أنفسنا."},
        {"value": "مصعد", "hint": "مثّل شيئًا ينقل الناس بين الطوابق."},
        {"value": "بطارية", "hint": "مثّل شيئًا يزوّد الأجهزة بالطاقة."},
        {"value": "خريطة", "hint": "مثّل شيئًا يساعد في معرفة الطرق والأماكن."},
        {"value": "متحف", "hint": "مثّل مكانًا يحفظ أشياء تاريخية أو فنية."},
        {"value": "عاصفة", "hint": "مثّل حالة جوية قوية فيها رياح شديدة."},
        {"value": "وصفة", "hint": "مثّل شيئًا نتبعه لتحضير طبق أو علاج."},
        {"value": "بطولة", "hint": "مثّل حدثًا تنافسيًا كبيرًا بين فرق أو لاعبين."},
    ],
    "hard": [
        {"value": "ضمير", "hint": "مثّل شيئًا معنويًا يرتبط بالحق والخطأ داخل الإنسان."},
        {"value": "دهشة", "hint": "مثّل شعورًا يظهر عند المفاجأة الشديدة."},
        {"value": "أسطورة", "hint": "مثّل قصة قديمة يختلط فيها الخيال بالحقيقة."},
        {"value": "فوضى", "hint": "مثّل حالة لا يوجد فيها ترتيب أو نظام."},
        {"value": "حنين", "hint": "مثّل شعورًا نحو ماضٍ أو أشخاص أو أماكن."},
        {"value": "مجازفة", "hint": "مثّل قرارًا فيه مخاطرة وعدم ضمان للنتيجة."},
        {"value": "عدالة", "hint": "مثّل قيمة ترتبط بالحق والإنصاف."},
        {"value": "فراغ", "hint": "مثّل حالة غياب الشيء أو الشعور بالخلو."},
        {"value": "إلهام", "hint": "مثّل حالة تدفع إلى فكرة أو إبداع جديد."},
        {"value": "هيبة", "hint": "مثّل شعورًا بالمكانة والوقار والاحترام."},
        {"value": "تناقض", "hint": "مثّل حالتين أو فكرتين لا تجتمعان بسهولة."},
        {"value": "ملل", "hint": "مثّل شعورًا يسببه التكرار والرتابة."},
    ],
}

ENTERTAINMENT_PROMPTS_BY_DIFFICULTY = {
    "easy": [
        {"value": "طاش ما طاش", "kind": "مسلسل"},
        {"value": "شباب البومب", "kind": "مسلسل"},
        {"value": "باب الحارة", "kind": "مسلسل"},
        {"value": "عمر وسلمى", "kind": "فيلم"},
        {"value": "عسل أسود", "kind": "فيلم"},
        {"value": "رسالة من تحت الماء", "kind": "أغنية"},
        {"value": "الأطلال", "kind": "أغنية"},
        {"value": "مدرسة المشاغبين", "kind": "مسرحية"},
        {"value": "العيال كبرت", "kind": "مسرحية"},
        {"value": "سك على بناتك", "kind": "مسرحية"},
        {"value": "مسرحية باي باي لندن", "kind": "مسرحية"},
        {"value": "ريا وسكينة", "kind": "مسلسل"},
    ],
    "medium": [
        {"value": "المال والبنون", "kind": "مسلسل"},
        {"value": "لن أعيش في جلباب أبي", "kind": "مسلسل"},
        {"value": "الزعيم", "kind": "فيلم"},
        {"value": "الكيف", "kind": "فيلم"},
        {"value": "البيضة والحجر", "kind": "فيلم"},
        {"value": "هو صحيح الهوى غلاب", "kind": "أغنية"},
        {"value": "سيرة الحب", "kind": "أغنية"},
        {"value": "بودي جارد", "kind": "مسرحية"},
        {"value": "الواد سيد الشغال", "kind": "مسرحية"},
        {"value": "جسمي لبّيس", "kind": "أغنية"},
        {"value": "ليالي الحلمية", "kind": "مسلسل"},
        {"value": "اللمبي", "kind": "فيلم"},
    ],
    "hard": [
        {"value": "خالتي صفية والدير", "kind": "مسلسل"},
        {"value": "التغريبة الفلسطينية", "kind": "مسلسل"},
        {"value": "شيء من الخوف", "kind": "فيلم"},
        {"value": "الأرض", "kind": "فيلم"},
        {"value": "الكيت كات", "kind": "فيلم"},
        {"value": "إنت عمري", "kind": "أغنية"},
        {"value": "على بالي", "kind": "أغنية"},
        {"value": "وجهة نظر", "kind": "مسرحية"},
        {"value": "لعبة الست", "kind": "فيلم"},
        {"value": "ضمير أبلة حكمت", "kind": "مسلسل"},
        {"value": "يانا يانا", "kind": "أغنية"},
        {"value": "ريا وسكينة", "kind": "مسرحية"},
    ],
}


def _build_hint(category: str, record: dict) -> str:
    if category == "ولا كلمة":
        media_kind = str(record.get("kind") or "عمل").strip()
        return (
            "يحتوي الباركود على اسم "
            f"{media_kind} "
            "للممثل فقط. مثّل العمل دون ذكر اسمه أو تهجئته."
        )
    return str(record.get("hint") or "مثّل الكلمة دون نطقها أو تهجئتها.").strip()


def _prompt_pool(category: str, difficulty: str) -> list[dict]:
    if category == "ولا كلمة":
        return ENTERTAINMENT_PROMPTS_BY_DIFFICULTY[difficulty]
    return GENERAL_PROMPTS_BY_DIFFICULTY[difficulty]


def fetch_prompt(category, difficulty):
    records = _prompt_pool(category, difficulty)
    debug_log("API RESPONSE", "Raw response received", records[:3])
    picked = choose_records(
        f"walla:{category}:{difficulty}",
        records,
        1,
        lambda item: source_record_id("walla_ar", category, item.get("value")),
    )[0]
    debug_log("WALLA", "Source record", picked)
    secret_value = str(picked.get("value") or "").strip()
    debug_log("WALLA", "Secret generated", secret_value)
    return {
        "id": source_record_id("walla_ar", category, secret_value),
        "difficulty": difficulty,
        "secret_value": secret_value,
        "secret_value_ar": secret_value,
        "display_hint_ar": _build_hint(category, picked),
        "metadata": {
            "content_kind": picked.get("kind") or "general",
            "language": "ar",
        },
    }
