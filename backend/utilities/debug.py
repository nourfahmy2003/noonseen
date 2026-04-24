"""Purpose: provide shared debug logging helpers for backend tracing."""

DEBUG = True


def debug_log(stage, message, data=None):
    if DEBUG:
        print(f"\n[DEBUG] {stage} → {message}")
        if data is not None:
            try:
                print(data)
            except Exception:
                print(str(data))


def debug_preview(data, limit=3):
    if isinstance(data, list):
        return data[:limit]
    if isinstance(data, tuple):
        return list(data[:limit])
    if isinstance(data, dict):
        items = list(data.items())[:limit]
        return {key: value for key, value in items}
    return data
