"""Purpose: fetch KalimaLab-backed live Arabic letter questions in reveal-only mode."""

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from backend.config import KALIMALAB_API_BASE, KALIMALAB_API_TOKEN
from backend.difficulty.rules import iter_difficulty_slots
from backend.normalization.questions import build_internal_question
from backend.services.repeat_prevention import choose_records
from backend.utilities.debug import debug_log, debug_preview
from backend.utilities.ids import source_record_id
from backend.utilities.text import first_visible_letter


def _fetch_words(limit=48):
    if not KALIMALAB_API_TOKEN:
        debug_log("API ERROR", "Request failed", "KalimaLab API key is not configured")
        raise ValueError("KalimaLab API key is not configured")

    request_url = f"{KALIMALAB_API_BASE}?limit={limit}"
    debug_log("API REQUEST", "Calling API", {"url": request_url, "params": {"limit": limit}})
    request = Request(
        request_url,
        headers={"Authorization": f"Bearer {KALIMALAB_API_TOKEN}", "User-Agent": "NoonJeem/1.0"},
    )
    try:
        with urlopen(request, timeout=12) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError) as error:
        debug_log("API ERROR", "Request failed", str(error))
        raise
    debug_log("API RESPONSE", "Raw response received", debug_preview(payload.get("data") if isinstance(payload, dict) else payload, limit=3))
    words = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(words, list) or len(words) < 6:
        debug_log("REJECTED", "Reason", "KalimaLab returned insufficient results")
        raise ValueError("KalimaLab returned insufficient results")
    return words


def fetch_questions(selection, source_definition, _cache):
    category = selection["backend_category"]
    words = choose_records(
        f"quiz:{category}",
        _fetch_words(),
        6,
        lambda entry: source_record_id("kalimalab", entry.get("id") or entry.get("arabic"), entry.get("root")),
    )
    prepared = []

    for index, ((difficulty, points), entry) in enumerate(zip(iter_difficulty_slots(), words), start=1):
        debug_log("RAW RECORD", "Incoming data", entry)
        answer = str(entry.get("arabic") or "").strip()
        root = str(entry.get("root") or "").strip()
        pattern = str(entry.get("pattern") or "").strip()
        pos = str(entry.get("pos") or "").strip()
        if not answer:
            debug_log("REJECTED", "Reason", "missing answer")
            continue
        record_id = source_record_id("kalimalab", entry.get("id") or answer, root or pattern or pos)
        first_letter = first_visible_letter(answer)

        if category == "لغة وأدب":
            question_ar = (
                f"ما الكلمة العربية التي جذرها {root or 'غير محدد'} وتصنيفها {pos or 'مفردة'}؟"
                if difficulty == "easy"
                else f"ما الكلمة العربية التي جذرها {root or 'غير محدد'} ووزنها {pattern or 'غير محدد'}؟"
                if difficulty == "medium"
                else f"ما الكلمة العربية التي جذرها {root or 'غير محدد'} ووزنها {pattern or 'غير محدد'} وتصنيفها {pos or 'غير محدد'}؟"
            )
        elif category == "حروف متحركة":
            question_ar = (
                f"ما الكلمة المشكولة التي تبدأ بحرف {first_letter}؟"
                if difficulty == "easy"
                else f"ما الكلمة المشكولة التي تبدأ بحرف {first_letter} وجذرها {root or 'غير محدد'}؟"
                if difficulty == "medium"
                else f"ما الكلمة المشكولة التي تبدأ بحرف {first_letter} ووزنها {pattern or 'غير محدد'} وتصنيفها {pos or 'غير محدد'}؟"
            )
        else:
            question_ar = (
                f"ما الكلمة العربية التي تبدأ بحرف {first_letter}؟"
                if difficulty == "easy"
                else f"ما الكلمة العربية التي تبدأ بحرف {first_letter} وجذرها {root or 'غير محدد'}؟"
                if difficulty == "medium"
                else f"ما الكلمة العربية التي تبدأ بحرف {first_letter} وجذرها {root or 'غير محدد'} ووزنها {pattern or 'غير محدد'}؟"
            )

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
                    "root": root,
                    "pattern": pattern,
                    "pos": pos,
                    "source_record_id": record_id,
                    "slot_index": index,
                },
            )
        )

    if len(prepared) != 6:
        debug_log("REJECTED", "Reason", "KalimaLab generator did not prepare 6 questions")
        raise ValueError("KalimaLab generator did not prepare 6 questions")
    debug_log("FINAL", "Questions ready", debug_preview(prepared, limit=5))
    return prepared
