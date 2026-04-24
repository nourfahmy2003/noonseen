"""Purpose: build reveal_visual logo challenges from API Ninjas using seeded live queries, pools, and intra-source spill."""

import re

from backend.api_adapters.api_ninjas_logo import fetch_api_ninjas_logo_payload
from backend.arabic.transform import normalize_arabic_text
from backend.difficulty.rules import iter_difficulty_slots, score_logo_record
from backend.normalization.questions import build_internal_question
from backend.services.repeat_prevention import choose_records
from backend.services.translation_service import translate_brand_answer_ar
from backend.source_clients.logo_brand_seeds import BRAND_LOGO_QUERY_SEEDS
from backend.utilities.debug import debug_log, debug_preview
from backend.utilities.ids import source_record_id, stable_hash


# Memoize brand translations inside one match preparation to avoid duplicate LibreTranslate calls.
_BRAND_NAME_AR_MEMO: dict[str, str] = {}


CORPORATE_SUFFIX_PATTERN = re.compile(
    r"\b(incorporated|inc|corp|corporation|company|co|group|holdings|holding|llc|ltd|limited|plc|ag|sa|nv|bv)\b\.?",
    re.I,
)


def _clean_company_name(value):
    cleaned = str(value or "").strip()
    cleaned = CORPORATE_SUFFIX_PATTERN.sub("", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip(" -_,.")
    return cleaned


def _cache_key(selection):
    return ("api_ninjas_logo", selection["backend_category"])


def _fetch_all_raw_records(selection, cache):
    """Purpose: fan out many explicit name/ticker queries because each response caps at 10 rows.
    
    API Ninjas Logo API returns at most 10 results per query. To build a robust pool
    for all difficulty levels (easy, medium, hard), we must use many seed queries.
    We fetch until we have accumulated enough raw records to fill 6 Jeopardy slots
    after normalization, translation, and quality filtering.
    """
    cache_key = _cache_key(selection)
    if cache_key in cache:
        debug_log("API REQUEST", "API Ninjas logo cycle cache hit", {"cache_key": cache_key})
        return cache[cache_key]

    debug_log(
        "API REQUEST",
        "Starting API Ninjas Logo seed queries",
        {
            "seed_query_count": len(BRAND_LOGO_QUERY_SEEDS),
            "preview_seeds": [f"{kind}:{val}" for kind, val in BRAND_LOGO_QUERY_SEEDS[:12]],
        },
    )

    records = []
    failed_queries = []
    
    for idx, (kind, seed) in enumerate(BRAND_LOGO_QUERY_SEEDS, start=1):
        try:
            params = {"name": seed} if kind == "name" else {"ticker": seed}
            debug_log(
                "API REQUEST",
                f"API Ninjas logo query ({idx}/{len(BRAND_LOGO_QUERY_SEEDS)})",
                {
                    "url": "https://api.api-ninjas.com/v1/logo",
                    "query_kind": kind,
                    "query_value": seed,
                    "params": params,
                },
            )
            payload = fetch_api_ninjas_logo_payload(**params)
            if isinstance(payload, list) and payload:
                records.extend(payload)
                debug_log(
                    "API RESPONSE",
                    f"API Ninjas returned {len(payload)} records for {kind}:{seed}",
                    {"batch_size": len(payload), "cumulative_total": len(records)},
                )
            else:
                debug_log(
                    "API RESPONSE",
                    f"API Ninjas returned empty or malformed response for {kind}:{seed}",
                    {"response_type": type(payload).__name__},
                )
        except Exception as error:
            debug_log("API ERROR", f"API Ninjas query failed for {kind}:{seed}", {"error": str(error)})
            failed_queries.append({"kind": kind, "seed": seed, "error": str(error)})
            continue

    cache[cache_key] = records
    debug_log(
        "FINAL",
        "API Ninjas raw data collection complete",
        {
            "total_raw_records": len(records),
            "seed_queries_attempted": len(BRAND_LOGO_QUERY_SEEDS),
            "failed_queries": len(failed_queries),
            "average_results_per_query": len(records) / max(len(BRAND_LOGO_QUERY_SEEDS), 1),
        },
    )
    if failed_queries:
        debug_log("WARNING", "Some API Ninjas queries failed", {"failed_samples": failed_queries[:3]})
    
    return records


def _normalize_logo_record(raw_record):
    debug_log("RAW RECORD", "Incoming logo row", raw_record)
    raw_name = _clean_company_name(raw_record.get("name"))
    ticker = str(raw_record.get("ticker") or "").strip().upper()
    image_url = str(raw_record.get("image") or "").strip()
    if not raw_name:
        debug_log("REJECTED", "Reason", {"reason": "missing company name", "raw_record": raw_record})
        return None
    if not image_url:
        debug_log("REJECTED", "Reason", {"reason": "missing logo image", "company_name": raw_name})
        return None

    try:
        memo_key = raw_name.strip().lower()
        if memo_key not in _BRAND_NAME_AR_MEMO:
            _BRAND_NAME_AR_MEMO[memo_key] = translate_brand_answer_ar(company_name_en=raw_name)
        answer_ar = normalize_arabic_text(_BRAND_NAME_AR_MEMO[memo_key])
    except Exception as error:
        debug_log(
            "REJECTED",
            "Reason",
            {"reason": "brand_translation_failed", "company_name": raw_name, "detail": str(error)},
        )
        return None

    normalized = {
        "id": source_record_id("apinjaslogo", raw_name, ticker or stable_hash(image_url)),
        "source_record_id": source_record_id("apinjaslogo", raw_name, ticker or stable_hash(image_url)),
        "company_name": raw_name,
        "ticker": ticker,
        "image_url": image_url,
        "answer_ar": answer_ar,
        "difficulty": score_logo_record(raw_name, ticker=ticker, image_url=image_url),
    }
    debug_log(
        "TRANSFORM",
        "Logo Arabic answer ready",
        {"source_answer": raw_name, "answer_ar": answer_ar, "difficulty": normalized["difficulty"]},
    )
    return normalized


def _build_logo_pools(selection, cache):
    """Build normalized pools segregated by difficulty.
    
    After fetching raw records:
    1. Normalize each record (clean name, get Arabic translation, fetch image)
    2. Deduplicate by ID
    3. Score each record for difficulty (easy/medium/hard)
    4. Build separate pools for each difficulty
    
    If a pool ends up too small, we log a warning but do NOT use local fallback.
    """
    normalized_records = []
    seen_ids = set()
    failed_normalizations = 0
    
    raw_records = _fetch_all_raw_records(selection, cache)
    debug_log(
        "NORMALIZATION",
        "Starting logo record normalization",
        {"raw_count": len(raw_records)},
    )
    
    for idx, raw_record in enumerate(raw_records, start=1):
        try:
            normalized = _normalize_logo_record(raw_record)
            if not normalized:
                failed_normalizations += 1
                continue
            if normalized["id"] in seen_ids:
                debug_log(
                    "DEDUPE",
                    "Skipping duplicate logo record",
                    {"id": normalized["id"], "company": normalized["company_name"]},
                )
                continue
            seen_ids.add(normalized["id"])
            normalized_records.append(normalized)
            if idx % 20 == 0:
                debug_log(
                    "PROGRESS",
                    f"Logo normalization progress: {idx}/{len(raw_records)}",
                    {"normalized_so_far": len(normalized_records), "failed": failed_normalizations},
                )
        except Exception as error:
            debug_log(
                "ERROR",
                "Unexpected error during logo normalization",
                {"raw_record_idx": idx, "error": str(error)},
            )
            failed_normalizations += 1
            continue

    # Build pools by difficulty.
    pools = {"easy": [], "medium": [], "hard": []}
    for record in normalized_records:
        pools.setdefault(record["difficulty"], []).append(record)

    debug_log(
        "FINAL",
        "Logo pools built from normalized records",
        {
            "total_normalized": len(normalized_records),
            "total_failed": failed_normalizations,
            "dedup_rate": f"{len(seen_ids)}/{len(raw_records)}",
            "pool_easy": len(pools["easy"]),
            "pool_medium": len(pools["medium"]),
            "pool_hard": len(pools["hard"]),
            "total_pooled": sum(len(v) for v in pools.values()),
        },
    )
    
    # Warn if any pool is dangerously small (though we won't fall back to local data).
    for diff, pool in pools.items():
        if len(pool) < 2:
            debug_log(
                "WARNING",
                f"Logo pool for difficulty {diff} is very small",
                {
                    "difficulty": diff,
                    "pool_size": len(pool),
                    "expected_minimum": 2,
                    "note": "Will attempt to use intra-source spill (no local fallback)",
                },
            )
    
    return pools


def _merge_spill_candidates(pools, difficulty, used_ids):
    """Purpose: prefer the native bucket, then borrow from the remaining difficulties (same live pool).
    
    For logo/brand challenges, we use intra-source spill when a difficulty pool
    runs low. The spill order is: preferred_difficulty → harder → easier.
    This allows medium-level brands to fill hard slots, for example.
    """
    order = {
        "easy": ("easy", "medium", "hard"),
        "medium": ("medium", "hard", "easy"),
        "hard": ("hard", "medium", "easy"),  # Prefer hard first for hard slots.
    }
    merged = []
    spill_breakdown = {d: 0 for d in ("easy", "medium", "hard")}
    
    for bucket in order[difficulty]:
        for row in pools.get(bucket, []):
            if row["id"] in used_ids:
                continue
            merged.append(row)
            spill_breakdown[bucket] += 1
    
    if spill_breakdown[difficulty] > 0:
        debug_log(
            "SPILL INFO",
            f"Logo spill for difficulty {difficulty}",
            {
                "preferred_difficulty": difficulty,
                "from_preferred": spill_breakdown[difficulty],
                "total_available": len(merged),
                "breakdown": spill_breakdown,
            },
        )
    else:
        debug_log(
            "SPILL WARNING",
            f"Logo preferred pool {difficulty} exhausted, borrowing from other difficulties",
            {
                "difficulty": difficulty,
                "total_spillable": len(merged),
                "breakdown": spill_breakdown,
            },
        )
    
    return merged


def fetch_questions(selection, source_definition, cache):
    """Build 6 reveal_visual logo challenges from API Ninjas seeded queries and intra-source spill.
    
    If any difficulty slot cannot be filled from the live API Ninjas data,
    we fail clearly with diagnostics (no local fallback allowed).
    """
    category = selection["backend_category"]
    debug_log(
        "SOURCE",
        "Live logo client starting",
        {"category": category, "client": "api_ninjas_logo"},
    )
    
    pools = _build_logo_pools(selection, cache)
    prepared = []
    used_ids = set()

    for slot_idx, (difficulty, points) in enumerate(iter_difficulty_slots(), start=1):
        merged = _merge_spill_candidates(pools, difficulty, used_ids)
        
        if not merged:
            # Provide comprehensive diagnostics for failures.
            total_available = sum(
                len([r for r in pool if r["id"] not in used_ids])
                for pool in pools.values()
            )
            debug_log(
                "FAILURE DIAGNOSTICS",
                f"Cannot fill logo slot {slot_idx}",
                {
                    "category": category,
                    "difficulty": difficulty,
                    "points": points,
                    "merged_available": len(merged),
                    "total_available_in_pools": total_available,
                    "used_so_far": len(used_ids),
                    "pool_status": {d: len(p) for d, p in pools.items()},
                },
            )
            raise ValueError(
                f"Not enough live records for quiz:logo:{category}:{difficulty}:{points}. "
                f"Available in all pools: {total_available}. Used so far: {len(used_ids)}. "
                f"Hint: ensure API Ninjas API key is valid (API_NINJAS_API_KEY) and seeded queries in "
                f"logo_brand_seeds.py return sufficient results. No local fallback is allowed."
            )

        picked = choose_records(
            f"quiz:logo:{category}:{difficulty}:{points}",
            merged,
            1,
            lambda record: record["id"],
        )[0]
        used_ids.add(picked["id"])
        
        debug_log(
            "FINAL",
            f"Logo/brand record chosen for slot {slot_idx}",
            {
                "slot": slot_idx,
                "difficulty": difficulty,
                "points": points,
                "company": picked["company_name"],
                "ticker": picked.get("ticker", ""),
                "answer_ar": picked["answer_ar"],
            },
        )

        visual_payload = {
            "type": "logo-image",
            "value": picked["image_url"],
            "fallbackText": picked["company_name"],
            "answerAr": picked["answer_ar"],
        }
        question = build_internal_question(
            question_id=picked["id"],
            category=category,
            difficulty=difficulty,
            points=points,
            question_ar="ما اسم هذه العلامة التجارية؟",
            answer_ar=picked["answer_ar"],
            source=source_definition["source"],
            source_type=source_definition["source_type"],
            metadata={
                "display_mode": "reveal_visual",
                "visual_type": "logo_or_brand",
                "visual_value": picked["image_url"],
                "visual_value_ar": picked["answer_ar"],
                "source_record_id": picked["source_record_id"],
                "visual": visual_payload,
            },
        )
        debug_log("SERIALIZER", f"Reveal visual payload produced for slot {slot_idx}", {"question_id": question["id"]})
        prepared.append(question)

    debug_log("FINAL", "Questions ready", debug_preview(prepared, limit=6))
    return prepared
