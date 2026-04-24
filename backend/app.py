"""Purpose: create and run the HTTP server used by the SeenJeem frontend."""

from http.server import ThreadingHTTPServer

from backend.config import HOST, PORT, PUBLIC_BASE_URL
from backend.routes.http_handler import SeenJeemHandler
from backend.utilities.debug import debug_log
from backend.utilities.network import detect_lan_ip


def create_server():
    return ThreadingHTTPServer((HOST, PORT), SeenJeemHandler)


def run_server():
    server = create_server()
    lan_ip = detect_lan_ip() or None
    debug_log("WALLA", "Server bind host/port", {"host": HOST, "port": PORT})
    debug_log("WALLA", "Detected LAN IP", lan_ip or "unavailable")

    print(f"Seen Jeem frontend running on http://{HOST}:{PORT}")
    if HOST == "0.0.0.0" and lan_ip:
        print(f"LAN access may be available at http://{lan_ip}:{PORT}")
    if PUBLIC_BASE_URL:
        print(f"Configured public base URL: {PUBLIC_BASE_URL}")
    elif lan_ip:
        print(f"Walla Kelma QR base will default to http://{lan_ip}:{PORT}")
    print("Runtime question preparation is live-source only. Local JSON banks are disabled.")
    print("IslamicQuizAPI now runs in-process inside the Seen Jeem backend.")
    print("Start the app with python3 server.py. Do not use python -m http.server for gameplay.")
    server.serve_forever()
