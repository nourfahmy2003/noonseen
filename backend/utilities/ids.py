"""Purpose: build stable source-based identifiers and hashes for live records."""

import hashlib


def stable_hash(*parts: object) -> str:
    payload = "||".join(str(part or "").strip() for part in parts)
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]


def source_record_id(prefix: str, *parts: object) -> str:
    cleaned = [str(part or "").strip().replace(" ", "_") for part in parts if str(part or "").strip()]
    if cleaned:
        return f"{prefix}:{':'.join(cleaned)}"
    return f"{prefix}:{stable_hash(prefix)}"
