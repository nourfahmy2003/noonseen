"""Purpose: live general trivia — The Trivia API for معلومات عامة only; Open Trivia DB for تاريخ/تكنولوجيا/عالم الحيوان; LibreTranslate/Lingva for Arabic."""

import html
import secrets
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import unquote

from backend.api_adapters.open_trivia import fetch_open_trivia_payload
from backend.api_adapters.the_trivia import fetch_the_trivia_payload
from backend.difficulty.rules import iter_difficulty_slots
from backend.normalization.questions import build_internal_question
from backend.services.repeat_prevention import choose_records
from backend.services.translation_service import translate_quiz_pair
from backend.services.trivia_quality import (
    combined_bucket,
    content_substance_score,
    should_keep_for_category,
)
from backend.config import LIBRETRANSLATE_API_KEY, LIBRETRANSLATE_BASE_URL, TRANSLATION_PROVIDER
from backend.utilities.debug import debug_log, debug_preview
from backend.utilities.ids import source_record_id, stable_hash


# The Trivia API v2 tags (English taxonomy) — used only for معلومات عامة.
THE_TRIVIA_GENERAL_TAGS = ("geography", "history", "science", "arts_and_literature")

# Open Trivia category ids for the three non-general Arabic columns.
OPENTDB_CATEGORY_BY_BACKEND = {
    "تاريخ": 23,
    "تكنولوجيا": 18,
    "عالم الحيوان": 27,
}

SLOT_POINTS = {"easy": [200, 200], "medium": [400, 400], "hard": [600, 600]}


def _lingva_primary_pool():
    """True when most rows will hit Lingva (GET) — tune batch sizes and avoid parallel translation."""
    if TRANSLATION_PROVIDER == "lingva":
        return True
    if TRANSLATION_PROVIDER == "libretranslate":
        return False
    if not LIBRETRANSLATE_BASE_URL:
        return True
    if "libretranslate.com" in LIBRETRANSLATE_BASE_URL.lower() and not (LIBRETRANSLATE_API_KEY or "").strip():
        return True
    return False


def _parallel_map_normalized(raw_rows, normalize_fn, prefix, category):
    """Normalize+translate rows. LibreTranslate uses a thread pool; Lingva is serialized globally."""
    if not raw_rows:
        return []
    if _lingva_primary_pool():
        out = []
        for raw in raw_rows:
            row = normalize_fn(prefix, category, raw)
            if row:
                out.append(row)
        return out

    max_workers = min(6, max(2, len(raw_rows)))
    out = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        future_map = {pool.submit(normalize_fn, prefix, category, raw): raw for raw in raw_rows}
        for future in as_completed(future_map):
            row = future.result()
            if row:
                out.append(row)
    return out


def _dedupe_translated_rows(rows):
    seen = set()
    out = []
    for row in rows:
        rid = row.get("id")
        if not rid or rid in seen:
            continue
        seen.add(rid)
        out.append(row)
    return out


def _decode_text(value):
    return html.unescape(unquote(str(value or ""))).strip()


def _normalize_the_trivia_records(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("results", "data", "questions"):
            if isinstance(payload.get(key), list):
                return payload[key]
    return []


def _fetch_the_trivia_pool(cache, categories, difficulty, limit):
    cache_key = ("the_trivia_pool", tuple(categories), difficulty, limit)
    if cache_key in cache:
        debug_log("API REQUEST", "The Trivia pool cache hit", {"cache_key": cache_key})
        return cache[cache_key]
    debug_log(
        "API REQUEST",
        "The Trivia v2 questions request",
        {
            "base_url": "configured THE_TRIVIA_API_BASE",
            "categories": categories,
            "difficulty": difficulty,
            "limit": limit,
        },
    )
    payload = fetch_the_trivia_payload(categories=list(categories), difficulty=difficulty, limit=limit)
    records = _normalize_the_trivia_records(payload)
    cache[cache_key] = records
    debug_log("FINAL", "The Trivia pool size", {"count": len(records), "difficulty": difficulty})
    return records


def _fetch_opentdb_pool(category_id, amount, difficulty=None):
    """Purpose: pull a single OpenTrivia page; callers loop to widen the live pool without local banks."""
    debug_log(
        "API REQUEST",
        "Open Trivia request",
        {
            "category_id": category_id,
            "amount": amount,
            "difficulty": difficulty or "mixed",
        },
    )
    payload = fetch_open_trivia_payload(
        category_id,
        amount=amount,
        difficulty=difficulty,
        session_token=None,
        question_type="multiple",
        cache_bust=secrets.token_hex(6),
    )
    results = payload.get("results") if isinstance(payload, dict) else None
    if payload.get("response_code") != 0 or not isinstance(results, list):
        raise ValueError(f"Open Trivia live source failed for category_id={category_id}")
    debug_log("FINAL", "Open Trivia pool size", {"count": len(results)})
    return results


def _normalize_the_trivia_row(prefix, category, raw_record):
    raw_question = raw_record.get("question")
    question_text = raw_question.get("text") if isinstance(raw_question, dict) else raw_question
    question_text = _decode_text(question_text)
    answer_text = _decode_text(raw_record.get("correctAnswer") or raw_record.get("correct_answer"))
    if not question_text or not answer_text:
        return None
    if not should_keep_for_category(category, question_text, answer_text):
        debug_log("REJECTED", "The Trivia row filtered pre-translation", {"reason": "weak_row", "preview": question_text[:80]})
        return None
    try:
        question_ar, answer_ar = translate_quiz_pair(question_en=question_text, answer_en=answer_text)
    except Exception as error:
        debug_log("REJECTED", "The Trivia translation failed", {"reason": str(error), "preview": question_text[:80]})
        return None

    record_id = source_record_id(prefix, category, raw_record.get("id") or stable_hash(question_text, answer_text))
    api_difficulty = raw_record.get("difficulty")
    bucket = combined_bucket(category, question_text, answer_text, api_difficulty)
    substance = content_substance_score(category, question_text, answer_text)
    return {
        "id": record_id,
        "question_ar": question_ar,
        "answer_ar": answer_ar,
        "bucket": bucket,
        "substance": substance,
        "source": "The Trivia API",
        "source_type": "api",
        "source_question": question_text,
        "source_answer": answer_text,
        "needs_review": False,
    }


def _normalize_opentdb_row(prefix, category, raw_record):
    question_text = _decode_text(raw_record.get("question"))
    answer_text = _decode_text(raw_record.get("correct_answer"))
    if not question_text or not answer_text:
        return None
    if not should_keep_for_category(category, question_text, answer_text):
        debug_log("REJECTED", "OpenTrivia row filtered pre-translation", {"reason": "weak_row", "preview": question_text[:80]})
        return None
    try:
        question_ar, answer_ar = translate_quiz_pair(question_en=question_text, answer_en=answer_text)
    except Exception as error:
        debug_log("REJECTED", "OpenTrivia translation failed", {"reason": str(error), "preview": question_text[:80]})
        return None

    record_id = source_record_id(prefix, category, stable_hash(question_text, answer_text))
    bucket = combined_bucket(category, question_text, answer_text, raw_record.get("difficulty"))
    substance = content_substance_score(category, question_text, answer_text)
    return {
        "id": record_id,
        "question_ar": question_ar,
        "answer_ar": answer_ar,
        "bucket": bucket,
        "substance": substance,
        "source": "Open Trivia DB",
        "source_type": "api",
        "source_question": question_text,
        "source_answer": answer_text,
        "needs_review": False,
    }


def _collect_the_trivia_translated(category, cache):
    """Pull generous batches per API difficulty for معلومات عامة, then rank inside buckets by substance.
    
    The Trivia API is used EXCLUSIVELY for معلومات عامة. We fetch medium/hard batches aggressively
    to avoid weak questions and ensure all difficulty slots are filled with quality content.
    """
    lingva_primary = _lingva_primary_pool()
    target = 48 if lingva_primary else 72
    early_stop = 22 if lingva_primary else 9999
    limits = (24, 32, 40) if lingva_primary else (50, 65, 80)
    collected = []
    for difficulty in ("hard", "medium", "easy"):
        for limit in limits:
            if len(collected) >= target:
                break
            raw_rows = _fetch_the_trivia_pool(cache, THE_TRIVIA_GENERAL_TAGS, difficulty, limit)
            collected.extend(_parallel_map_normalized(raw_rows, _normalize_the_trivia_row, "thetrivia", category))
            if len(_dedupe_translated_rows(collected)) >= early_stop:
                break
        if len(collected) >= target or len(_dedupe_translated_rows(collected)) >= early_stop:
            break

    deduped = _dedupe_translated_rows(collected)
    debug_log(
        "FINAL",
        "The Trivia collection stats for معلومات عامة",
        {"total_collected": len(collected), "target": target, "after_dedup": len(deduped)},
    )
    return deduped


def _collect_opentdb_translated(category, _cache):
    """Pull multiple mixed batches (new session tokens) until enough Arabic rows survive filtering.
    
    For تاريخ, تكنولوجيا, and عالم الحيوان, we need to be aggressive about quality filtering.
    We fetch many batches to ensure that after translation and quality validation,
    we have enough high-substance rows to fill all difficulty slots properly.
    """
    lingva_primary = _lingva_primary_pool()
    # Lingva is slow and rate-limited: smaller OpenTrivia pages + stop as soon as the pool is viable.
    rounds = 8 if lingva_primary else 8
    amounts = (16, 20) if lingva_primary else (50, 60)
    cap = 120 if lingva_primary else 96
    early_stop = 22 if lingva_primary else 9999

    cat_id = OPENTDB_CATEGORY_BY_BACKEND[category]
    collected = []

    for _round in range(rounds):
        for amount in amounts:
            raw_rows = _fetch_opentdb_pool(cat_id, amount, difficulty=None)
            collected.extend(_parallel_map_normalized(raw_rows, _normalize_opentdb_row, "opentdb", category))
            if len(_dedupe_translated_rows(collected)) >= early_stop:
                break
        if len(collected) >= cap or len(_dedupe_translated_rows(collected)) >= early_stop:
            break

    deduped = _dedupe_translated_rows(collected)
    debug_log(
        "FINAL",
        f"Open Trivia collection stats for {category}",
        {"total_collected": len(collected), "target": cap, "after_dedup": len(deduped)},
    )
    return deduped


def _bucketize(records):
    pools = {"easy": [], "medium": [], "hard": []}
    for record in records:
        pools.setdefault(record["bucket"], []).append(record)
    for key in pools:
        pools[key].sort(key=lambda row: row["substance"], reverse=True)
    debug_log(
        "FINAL",
        "Trivia bucket sizes after translation",
        {k: len(v) for k, v in pools.items()},
    )
    return pools


def _pick_with_spill(namespace, pools, difficulty, need, used_ids):
    """Prefer the exact bucket, then spill across other buckets using the same live pool."""
    spill_order = {"easy": ("easy", "medium", "hard"), "medium": ("medium", "hard", "easy"), "hard": ("hard", "medium", "easy")}
    merged = []
    for bucket in spill_order[difficulty]:
        merged.extend([row for row in pools.get(bucket, []) if row["id"] not in used_ids])
    if len(merged) < need:
        debug_log("REJECTED", "Not enough rows even after spill", {"difficulty": difficulty, "have": len(merged), "need": need})
        raise ValueError(f"Not enough validated Arabic live questions for {namespace}")
    picked = choose_records(namespace, merged, need, lambda row: row["id"])
    for row in picked:
        used_ids.add(row["id"])
    return picked


def fetch_questions(selection, source_definition, cache):
    category = selection["backend_category"]
    debug_log("SOURCE", "Live trivia client start", {"category": category, "client": "the_trivia"})

    if category == "معلومات عامة":
        records = _collect_the_trivia_translated(category, cache)
    elif category in OPENTDB_CATEGORY_BY_BACKEND:
        records = _collect_opentdb_translated(category, cache)
    else:
        raise ValueError(f"No live trivia routing configured for {category}")

    if len(records) < 6:
        raise ValueError(
            f"Not enough translated trivia rows for {category} (have {len(records)}, need 6). "
            "Configure LIBRETRANSLATE_BASE_URL + LIBRETRANSLATE_API_KEY for reliable translation, "
            "or use TRANSLATION_PROVIDER=hybrid without a LibreTranslate URL (Lingva; may rate-limit)."
        )

    pools = _bucketize(records)
    prepared = []
    used_ids = set()

    for difficulty, _ in iter_difficulty_slots()[::2]:
        picked = _pick_with_spill(
            f"quiz:general:{category}:{difficulty}",
            pools,
            difficulty,
            2,
            used_ids,
        )
        for points, record in zip(SLOT_POINTS[difficulty], picked):
            prepared.append(
                build_internal_question(
                    question_id=record["id"],
                    category=category,
                    difficulty=difficulty,
                    points=points,
                    question_ar=record["question_ar"],
                    answer_ar=record["answer_ar"],
                    source=record["source"],
                    source_type=record["source_type"],
                    metadata={
                        "display_mode": "reveal_answer",
                        "source_record_id": record["id"],
                        "source_question": record["source_question"],
                        "source_answer": record["source_answer"],
                    },
                    needs_review=record["needs_review"],
                )
            )

    if len(prepared) != 6:
        raise ValueError(f"{category} must return exactly 6 validated live questions")

    debug_log("FINAL", "Questions ready", debug_preview(prepared, limit=5))
    return prepared
