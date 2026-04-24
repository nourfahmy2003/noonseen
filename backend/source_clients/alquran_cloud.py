"""Purpose: fetch live Quran-derived letter questions from AlQuran Cloud only."""

from backend.arabic.transform import normalize_arabic_text
from backend.config import ALQURAN_CLOUD_API_BASE
from backend.difficulty.rules import iter_difficulty_slots
from backend.normalization.questions import build_internal_question
from backend.services.repeat_prevention import choose_records
from backend.utilities.debug import debug_log, debug_preview
from backend.utilities.ids import source_record_id
from backend.utilities.http import fetch_json
from backend.utilities.text import first_visible_letter


SURAH_ENDPOINT = f"{ALQURAN_CLOUD_API_BASE}/surah"


def fetch_questions(selection, source_definition, cache):
    category = selection["backend_category"]
    if cache.get("alquran_surahs") is None:
        debug_log("API REQUEST", "Calling API", {"url": SURAH_ENDPOINT, "params": None})
        payload = fetch_json(SURAH_ENDPOINT)
        debug_log("API RESPONSE", "Raw response received", debug_preview(payload.get("data") if isinstance(payload, dict) else payload, limit=3))
        surahs = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(surahs, list) or len(surahs) < 6:
            debug_log("REJECTED", "Reason", "AlQuran Cloud returned insufficient surah data")
            raise ValueError("AlQuran Cloud returned insufficient surah data")
        cache["alquran_surahs"] = surahs

    surahs = choose_records(
        f"quiz:{category}",
        cache["alquran_surahs"],
        6,
        lambda surah: source_record_id("alquran", surah.get("number"), surah.get("numberOfAyahs")),
    )
    prepared = []
    for index, ((difficulty, points), surah) in enumerate(zip(iter_difficulty_slots(), surahs), start=1):
        debug_log("RAW RECORD", "Incoming data", surah)
        answer = normalize_arabic_text(surah.get("name"))
        if not answer:
            debug_log("REJECTED", "Reason", "missing answer")
            continue

        revelation_type = "مكية" if str(surah.get("revelationType") or "").lower().startswith("meccan") else "مدنية"
        ayahs = int(surah.get("numberOfAyahs") or 0)
        first_letter = first_visible_letter(answer)
        if difficulty == "easy":
            question_ar = f"ما اسم السورة التي تبدأ بحرف {first_letter}؟"
        elif difficulty == "medium":
            question_ar = f"ما السورة التي تبدأ بحرف {first_letter} وهي سورة {revelation_type}؟"
        else:
            question_ar = f"ما السورة التي تبدأ بحرف {first_letter} وعدد آياتها {ayahs}؟"

        record_id = source_record_id("alquran", surah.get("number"), surah.get("englishName"))
        debug_log(
            "TRANSFORM",
            "Built question",
            {"question_ar": question_ar, "answer_ar": answer, "difficulty": difficulty, "slot_index": index},
        )
        prepared.append(
            build_internal_question(
                question_id=record_id,
                category=category,
                difficulty=difficulty,
                points=points,
                question_ar=question_ar,
                answer_ar=answer,
                source=source_definition["source"],
                source_type=source_definition["source_type"],
                metadata={
                    "display_mode": "reveal_answer",
                    "revelation_type": revelation_type,
                    "ayah_count": ayahs,
                    "source_record_id": record_id,
                    "surah_number": surah.get("number"),
                    "slot_index": index,
                },
            )
        )

    if len(prepared) != 6:
        debug_log("REJECTED", "Reason", "AlQuran Cloud generator did not prepare 6 questions")
        raise ValueError("AlQuran Cloud generator did not prepare 6 questions")
    debug_log("FINAL", "Questions ready", debug_preview(prepared, limit=5))
    return prepared
