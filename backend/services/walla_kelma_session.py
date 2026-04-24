"""Purpose: store short-lived Walla Kelma sessions in memory without exposing secrets publicly."""

import secrets
import time

from backend.config import WALLA_KELMA_SESSION_TTL_SECONDS


SESSIONS = {}


def _purge_expired_sessions():
    now = int(time.time())
    expired = [token for token, session in SESSIONS.items() if int(session.get("expires_at") or 0) <= now]
    for token in expired:
        SESSIONS.pop(token, None)


def create_session(prompt):
    _purge_expired_sessions()
    token = secrets.token_urlsafe(18)
    expires_at = int(time.time()) + WALLA_KELMA_SESSION_TTL_SECONDS
    SESSIONS[token] = {
        "token": token,
        "prompt": prompt,
        "status": "active",
        "expires_at": expires_at,
    }
    return SESSIONS[token]


def get_session(token):
    _purge_expired_sessions()
    session = SESSIONS.get(token)
    if not session:
        raise ValueError("Walla Kelma session was not found or has expired.")
    return session


def complete_session(token):
    session = get_session(token)
    session["status"] = "completed"
    return session
