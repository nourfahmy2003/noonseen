"""Purpose: resolve LAN-reachable host information for public Seen Jeem links."""

import socket
from urllib.parse import urlparse


def is_loopback_host(host):
    normalized = str(host or "").strip().lower()
    return normalized.startswith("127.") or normalized in {"localhost", "::1", "[::1]"}


def extract_host_name(value):
    host = str(value or "").strip()
    if not host:
        return ""
    if "://" in host:
        return urlparse(host).hostname or ""
    if host.startswith("[") and "]" in host:
        return host[1 : host.index("]")]
    return host.split(":", 1)[0]


def detect_lan_ip():
    """Resolve the preferred outbound LAN IP without depending on hostname DNS."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.connect(("8.8.8.8", 80))
            return probe.getsockname()[0]
    except OSError:
        try:
            candidate = socket.gethostbyname(socket.gethostname())
        except OSError:
            return ""
        return "" if is_loopback_host(candidate) else candidate
