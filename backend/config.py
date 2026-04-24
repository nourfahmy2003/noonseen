"""Purpose: centralize the live runtime configuration used by quiz preparation."""

import os
from pathlib import Path


HOST = os.environ.get("SEENJEEM_HOST", "0.0.0.0")
PORT = int(os.environ.get("SEENJEEM_PORT", "8000"))

ROOT = Path(__file__).resolve().parent.parent

# Translation: LibreTranslate is required for general-style quiz text (no heuristic fallback).
TRANSLATION_PROVIDER = os.environ.get("TRANSLATION_PROVIDER", "libretranslate").strip().lower()
# Example host only: https://libretranslate.com — the adapter appends `/translate` itself.
LIBRETRANSLATE_BASE_URL = os.environ.get("LIBRETRANSLATE_BASE_URL", "").strip().rstrip("/")
LIBRETRANSLATE_API_KEY = os.environ.get("LIBRETRANSLATE_API_KEY", "").strip()

# Live source endpoints used at runtime. Islamic categories now run from the
# same backend process through an in-process provider instead of a second server.
REST_COUNTRIES_API_BASE = "https://restcountries.com/v3.1"
OPEN_TRIVIA_API_BASE = "https://opentdb.com/api.php"
THE_TRIVIA_API_BASE = os.environ.get("THE_TRIVIA_API_BASE", "https://the-trivia-api.com/v2/questions")
THE_TRIVIA_API_KEY = os.environ.get("THE_TRIVIA_API_KEY", "").strip()
ALQURAN_CLOUD_API_BASE = "https://api.alquran.cloud/v1"
KALIMALAB_API_BASE = os.environ.get("KALIMALAB_API_BASE", "https://api.kalimalab.com/v1/words")
DATAMUSE_API_BASE = "https://api.datamuse.com/words"
TMDB_API_BASE = "https://api.themoviedb.org/3"
AUDIO_DB_API_BASE = os.environ.get("AUDIODB_API_BASE", "https://www.theaudiodb.com/api/v1/json")
API_FOOTBALL_API_BASE = os.environ.get("API_FOOTBALL_API_BASE", "https://v3.football.api-sports.io")
API_NINJAS_LOGO_API_BASE = os.environ.get("API_NINJAS_LOGO_API_BASE", "https://api.api-ninjas.com/v1/logo")
API_COUNTRIES_API_BASE = os.environ.get("API_COUNTRIES_API_BASE", "https://www.apicountries.com")

# Tokens are optional per source. Missing credentials do not trigger local
# fallback; the corresponding live category simply becomes unavailable.
KALIMALAB_API_TOKEN = os.environ.get("KALIMALAB_API_KEY") or os.environ.get("KALIMALAB_TOKEN")
TMDB_BEARER_TOKEN = os.environ.get("TMDB_BEARER_TOKEN") or os.environ.get("TMDB_API_TOKEN")
API_FOOTBALL_API_KEY = os.environ.get("API_FOOTBALL_API_KEY")
# API Ninjas key must be supplied via environment (never commit real keys into the repo).
API_NINJAS_API_KEY = os.environ.get("API_NINJAS_API_KEY", "").strip()
AUDIO_DB_API_KEY = os.environ.get("AUDIODB_API_KEY", "2")
WALLA_KELMA_SESSION_TTL_SECONDS = int(os.environ.get("WALLA_KELMA_SESSION_TTL_SECONDS", "900"))
# Leave the public base empty by default so QR/session links can derive the
# actual LAN-reachable host from runtime instead of a stale hardcoded IP.
PUBLIC_BASE_URL = os.environ.get("SEENJEEM_PUBLIC_BASE_URL", "").strip()
