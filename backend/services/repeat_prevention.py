"""Purpose: prefer unseen live records first and reduce near-term repeats in memory."""

import random
from collections import defaultdict, deque

from backend.utilities.debug import debug_log


RECENT_RECORD_IDS: dict[str, deque[str]] = defaultdict(lambda: deque(maxlen=120))


def _dedupe_records(records, id_fn):
    deduped = []
    seen = set()
    for record in records:
        record_id = id_fn(record)
        if not record_id or record_id in seen:
            debug_log("FILTER", "Duplicate removed", record_id or "missing_id")
            continue
        seen.add(record_id)
        deduped.append(record)
    return deduped


def choose_records(namespace, records, amount, id_fn):
    unique_records = _dedupe_records(records, id_fn)
    debug_log(
        "FILTER",
        f"Choosing records for namespace {namespace}",
        {"incoming": len(records), "unique": len(unique_records), "amount": amount},
    )
    if len(unique_records) < amount:
        raise ValueError(f"Not enough live records for {namespace}")

    shuffled = unique_records[:]
    random.shuffle(shuffled)
    recent_ids = set(RECENT_RECORD_IDS[namespace])
    unseen = [record for record in shuffled if id_fn(record) not in recent_ids]
    remaining = [record for record in shuffled if id_fn(record) in recent_ids]
    picked = (unseen + remaining)[:amount]
    RECENT_RECORD_IDS[namespace].extend(id_fn(record) for record in picked)
    debug_log(
        "FINAL",
        f"Picked records for namespace {namespace}",
        [id_fn(record) for record in picked],
    )
    return picked
