"""Purpose: provide shared HTTP, JSON, and request URL helpers for handlers and adapters."""

import json
import socket
import ssl
import time
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from backend.config import PUBLIC_BASE_URL
from backend.utilities.debug import debug_log, debug_preview
from backend.utilities.network import detect_lan_ip, extract_host_name, is_loopback_host


SENSITIVE_HEADER_KEYS = {"authorization", "x-api-key", "api-key"}


def _redact_headers(headers):
    sanitized = {}
    for key, value in (headers or {}).items():
        sanitized[key] = "<redacted>" if key.lower() in SENSITIVE_HEADER_KEYS else value
    return sanitized


def _has_auth_header(headers):
    normalized = {str(key).lower(): value for key, value in (headers or {}).items()}
    return bool(normalized.get("authorization") or normalized.get("x-api-key") or normalized.get("api-key"))


def json_response(handler, payload, status=200):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def send_bytes_response(handler, payload, status=200, content_type="application/json"):
    handler.send_response(status)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(payload)))
    handler.end_headers()
    handler.wfile.write(payload)


def read_json_body(handler):
    content_length = int(handler.headers.get("Content-Length", "0") or "0")
    if content_length <= 0:
        return {}

    payload = handler.rfile.read(content_length)
    try:
        return json.loads(payload.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


def get_public_base_url(handler):
    forwarded_proto = str(handler.headers.get("X-Forwarded-Proto") or "").strip()
    host = str(handler.headers.get("Host") or "").strip()
    protocol = forwarded_proto or "http"
    configured_base = PUBLIC_BASE_URL.rstrip("/")
    if configured_base and not is_loopback_host(extract_host_name(configured_base)):
        return configured_base

    if host and not is_loopback_host(extract_host_name(host)):
        return f"{protocol}://{host}"

    lan_ip = detect_lan_ip()
    if lan_ip:
        port = getattr(getattr(handler, "server", None), "server_port", None) or 8000
        return f"{protocol}://{lan_ip}:{port}"

    return configured_base


def fetch_json(
    url,
    user_agent="NoonJeem/1.0",
    timeout=12,
    headers=None,
    query=None,
    max_attempts=1,
    retry_backoff_seconds=(),
    retry_on_statuses=None,
):
    request_headers = {"User-Agent": user_agent}
    if headers:
        request_headers.update(headers)
    request_url = url
    if query:
        separator = "&" if "?" in request_url else "?"
        request_url = f"{request_url}{separator}{urlencode(query, doseq=True)}"
    attempts = max(1, int(max_attempts or 1))
    retry_statuses = set(retry_on_statuses or ())
    debug_log(
        "API REQUEST",
        "Calling API",
        {
            "url": url,
            "final_url": request_url,
            "params": query,
            # Never print raw auth material into the debug trace.
            "headers": _redact_headers(request_headers),
            "has_auth_header": _has_auth_header(request_headers),
            "max_attempts": attempts,
        },
    )

    for attempt in range(1, attempts + 1):
        request = Request(request_url, headers=request_headers)
        try:
            with urlopen(request, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
                debug_log("API RESPONSE", "Raw response received", debug_preview(payload, limit=3))
                return payload
        except HTTPError as error:
            if error.code in retry_statuses and attempt < attempts:
                delay_seconds = (
                    retry_backoff_seconds[min(attempt - 1, len(retry_backoff_seconds) - 1)]
                    if retry_backoff_seconds
                    else 1.0
                )
                debug_log(
                    "API REQUEST",
                    "Retrying after HTTP error",
                    {"status": error.code, "attempt": attempt, "next_delay_seconds": delay_seconds},
                )
                time.sleep(delay_seconds)
                continue
            error_message = f"Live source request failed with HTTP {error.code}: {request_url}"
            debug_log("API ERROR", "Request failed", error_message)
            raise ValueError(error_message) from error
        except URLError as error:
            if attempt < attempts:
                delay_seconds = (
                    retry_backoff_seconds[min(attempt - 1, len(retry_backoff_seconds) - 1)]
                    if retry_backoff_seconds
                    else 1.0
                )
                debug_log(
                    "API REQUEST",
                    "Retrying after URL error",
                    {"attempt": attempt, "next_delay_seconds": delay_seconds, "reason": str(error)},
                )
                time.sleep(delay_seconds)
                continue
            error_message = f"Live source is unreachable: {request_url}"
            debug_log("API ERROR", "Request failed", error_message)
            raise ValueError(error_message) from error
        except (TimeoutError, socket.timeout, ssl.SSLError, ConnectionResetError) as error:
            if attempt < attempts:
                delay_seconds = (
                    retry_backoff_seconds[min(attempt - 1, len(retry_backoff_seconds) - 1)]
                    if retry_backoff_seconds
                    else 1.0
                )
                debug_log(
                    "API REQUEST",
                    "Retrying after network timeout",
                    {"attempt": attempt, "next_delay_seconds": delay_seconds, "reason": str(error)},
                )
                time.sleep(delay_seconds)
                continue
            error_message = f"Live source timed out: {request_url}"
            debug_log("API ERROR", "Request failed", error_message)
            raise ValueError(error_message) from error


def fetch_json_post(
    url,
    payload,
    user_agent="NoonJeem/1.0",
    timeout=25,
    headers=None,
    max_attempts=1,
    retry_backoff_seconds=(),
    retry_on_statuses=None,
):
    """Purpose: POST JSON bodies (LibreTranslate, etc.) with the same logging/redaction rules as GET."""
    request_headers = {
        "User-Agent": user_agent,
        "Content-Type": "application/json; charset=utf-8",
    }
    if headers:
        request_headers.update(headers)
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    attempts = max(1, int(max_attempts or 1))
    retry_statuses = set(retry_on_statuses or ())
    debug_log(
        "API REQUEST",
        "Calling API (POST JSON)",
        {
            "url": url,
            "body_keys": sorted(str(key) for key in (payload or {}).keys()),
            "headers": _redact_headers(request_headers),
            "has_auth_header": _has_auth_header(request_headers),
            "max_attempts": attempts,
        },
    )

    for attempt in range(1, attempts + 1):
        request = Request(url, data=body, headers=request_headers, method="POST")
        try:
            with urlopen(request, timeout=timeout) as response:
                parsed = json.loads(response.read().decode("utf-8"))
                debug_log("API RESPONSE", "Raw response received", debug_preview(parsed, limit=3))
                return parsed
        except HTTPError as error:
            if error.code in retry_statuses and attempt < attempts:
                delay_seconds = (
                    retry_backoff_seconds[min(attempt - 1, len(retry_backoff_seconds) - 1)]
                    if retry_backoff_seconds
                    else 1.0
                )
                debug_log(
                    "API REQUEST",
                    "Retrying POST after HTTP error",
                    {"status": error.code, "attempt": attempt, "next_delay_seconds": delay_seconds},
                )
                time.sleep(delay_seconds)
                continue
            error_message = f"Live source POST failed with HTTP {error.code}: {url}"
            debug_log("API ERROR", "Request failed", error_message)
            raise ValueError(error_message) from error
        except URLError as error:
            if attempt < attempts:
                delay_seconds = (
                    retry_backoff_seconds[min(attempt - 1, len(retry_backoff_seconds) - 1)]
                    if retry_backoff_seconds
                    else 1.0
                )
                debug_log(
                    "API REQUEST",
                    "Retrying POST after URL error",
                    {"attempt": attempt, "next_delay_seconds": delay_seconds, "reason": str(error)},
                )
                time.sleep(delay_seconds)
                continue
            error_message = f"Live source POST is unreachable: {url}"
            debug_log("API ERROR", "Request failed", error_message)
            raise ValueError(error_message) from error
        except (TimeoutError, socket.timeout, ssl.SSLError, ConnectionResetError) as error:
            if attempt < attempts:
                delay_seconds = (
                    retry_backoff_seconds[min(attempt - 1, len(retry_backoff_seconds) - 1)]
                    if retry_backoff_seconds
                    else 1.0
                )
                debug_log(
                    "API REQUEST",
                    "Retrying POST after network timeout",
                    {"attempt": attempt, "next_delay_seconds": delay_seconds, "reason": str(error)},
                )
                time.sleep(delay_seconds)
                continue
            error_message = f"Live source POST timed out: {url}"
            debug_log("API ERROR", "Request failed", error_message)
            raise ValueError(error_message) from error
