# NoonJeem / Seen Jeem

Arabic quiz and **ولا كلمة** (Walla Kelma) party game. A small **Python** backend serves static pages and **live-only** APIs (no bundled question bank fallback at runtime). The UI is plain **HTML / CSS / JavaScript** with a **quiz-feature** module for category flows and React-style pieces where noted.

---

## Requirements

- **Python 3** (stdlib only for the server; third-party usage is via HTTP to external APIs).
- **Network access** (questions and translations are fetched from live services).
- Optional: **[cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/)** for public URLs and phone QR (see below).

Install optional local dependency (Cloudflare tunnel helper via npm):

```bash
npm install
```

This adds the `cloudflared` npm wrapper; you can also install the official `cloudflared` binary with Homebrew if you prefer.

---

## Quick start (local)

From the repository root:

```bash
python3 server.py
```

By default the app binds to **`0.0.0.0:8000`**, so you can open:

- **This machine:** [http://localhost:8000](http://localhost:8000)
- **Same LAN:** `http://<your-lan-ip>:8000` (the server prints hints when it can detect a LAN IP).

**Do not** serve the folder with `python -m http.server` for full gameplay; the game expects the custom handler and `/api/*` routes.

### Environment variables (optional but important for some modes)

| Variable | Purpose |
|----------|---------|
| `SEENJEEM_HOST` | Bind host (default `0.0.0.0`). |
| `SEENJEEM_PORT` | Port (default `8000`). |
| `SEENJEEM_PUBLIC_BASE_URL` | **Public base URL** used in QR and Walla Kelma links (no trailing slash). Set this when using Cloudflare Tunnel or any HTTPS reverse proxy. |
| `LIBRETRANSLATE_BASE_URL` | LibreTranslate instance URL (translation for many quiz categories). |
| `LIBRETRANSLATE_API_KEY` | If your LibreTranslate instance requires a key. |
| `THE_TRIVIA_API_KEY` | The Trivia API key (e.g. for معلومات عامة and related flows). |
| `API_NINJAS_API_KEY` | For **شعارات وعلامات تجارية** (logo API). |
| `KALIMALAB_API_KEY` / `KALIMALAB_TOKEN` | KalimaLab-backed categories. |
| `TMDB_BEARER_TOKEN` | TMDB-backed Walla Kelma / media flows. |
| `API_FOOTBALL_API_KEY` | Football-related Walla Kelma. |

See `backend/config.py` for the full list and defaults. Missing keys usually mean **that category is unavailable**, not a local JSON fallback.

---

## Running Seen Jeem with Cloudflare Tunnel (QR works on phone)

### Why use this

- Fixes **QR codes not working on the phone** when they pointed at a LAN IP or wrong origin.
- Works across devices (same Wi‑Fi or different networks).
- Avoids fighting **local IP / firewall** issues for guests.

### Step 1 — Start your app

```bash
python3 server.py
```

Ensure the app is reachable at **http://localhost:8000** (or the port you set with `SEENJEEM_PORT`).

### Step 2 — Start Cloudflare Tunnel

In a **second** terminal:

```bash
cloudflared tunnel --url http://localhost:8000
```

(If you use the npm-installed helper, check `npx cloudflared --help` for the equivalent command on your system.)

### Step 3 — Copy your public URL

The tunnel prints a URL similar to:

`https://random-name.trycloudflare.com`

### Step 4 — Set it as your base URL (critical for QR)

```bash
export SEENJEEM_PUBLIC_BASE_URL="https://random-name.trycloudflare.com"
```

Then **restart** the Python server:

```bash
python3 server.py
```

The backend exposes this base URL to the UI (e.g. via `/api/quiz/live-subcategories`) so generated links match what phones can open.

### Step 5 — Use QR on the phone

QR codes should now encode links like:

`https://random-name.trycloudflare.com/walla-kelma.html?token=XXXX`

Scan on the phone → it should load correctly.

### Every time you restart

1. Run the server: `python3 server.py`
2. Run the tunnel: `cloudflared tunnel --url http://localhost:8000`
3. Copy the **new** URL (quick tunnels change each run unless you configure a **named** tunnel).
4. Export again: `export SEENJEEM_PUBLIC_BASE_URL="NEW_URL"` and restart `python3 server.py`.

### Notes

- **Quick tunnel URLs change** each time unless you set up a permanent Cloudflare tunnel.
- Keep the **tunnel terminal** open while testing.
- If the tunnel stops, **QR / public links stop working** until you bring the tunnel (and matching `SEENJEEM_PUBLIC_BASE_URL`) back.

---

## Repository structure

High-level map of how the code is organized.

### Root

| Path | Role |
|------|------|
| `server.py` | Entry point: calls `backend.app.run_server()`. |
| `index.html`, `board.html`, `categories.html`, `results.html`, `walla-kelma.html` | Main static shells and game pages. |
| `game.js`, `style.css` | Core client game logic and global styles. |
| `package.json` / `package-lock.json` | Optional npm deps (e.g. `cloudflared` helper). |
| `IMPLEMENTATION_SUMMARY.md` | Engineering notes on recent category / API / quality changes. |

### `assets/`

Static images and shared front-end assets (e.g. branding).

### `backend/` — Python server and logic

| Path | Role |
|------|------|
| `app.py` | Builds `ThreadingHTTPServer`, prints URLs and startup hints. |
| `config.py` | **Single config hub:** host/port, `PUBLIC_BASE_URL`, external API bases, API keys from environment. |
| `routes/http_handler.py` | **`SeenJeemHandler`:** static file serving from repo root + **API routes** (CORS headers, POST/GET handlers). |
| `source_registry.py` | Maps **UI Arabic category names** → `SourceDefinition` (which client, auth required, quiz vs walla_kelma). |
| `api_adapters/` | Thin HTTP clients for external APIs (Open Trivia, The Trivia API, LibreTranslate, REST Countries, API Ninjas logos, Islamic quiz API, etc.). |
| `source_clients/` | Higher-level **fetch / normalize** logic per source; used when preparing live question banks. |
| `services/` | **Domain services:** `quiz_preparation` (match bank), `translation_service`, `trivia_quality`, country/letter generators, **Walla Kelma** session + completion, board serialization, repeat prevention, category mapping, etc. |
| `models/schemas.py` | Shared typed shapes (e.g. source definitions, payloads). |
| `data/` | In-repo **reference data** (e.g. letter/country banks) used together with live APIs—not a full offline replacement for runtime trivia. |
| `normalization/` | Question text normalization helpers. |
| `arabic/` | Arabic text transforms and labeling helpers. |
| `difficulty/` | Rules for difficulty assignment / bucketing. |
| `local_datasets/` | Curated or reviewed JSON used where applicable (e.g. reviewed content). |
| `utilities/` | HTTP helpers (`get_public_base_url`, JSON responses), debug logging, IDs, text, network (LAN IP detection). |

#### Main HTTP API (under `SeenJeemHandler`)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/quiz/live-subcategories` | Lists subcategories available live, plus **`publicBaseUrl`** for clients. |
| POST | `/api/quiz/prepare-match` | Body: `selectedSubcategories` → returns prepared **`questionBank`** and diagnostics. |
| POST | `/api/walla-kelma/create` | Creates a Walla Kelma session from selected subcategory / difficulty. |
| GET | `/api/walla-kelma/session/<token>` | Fetches private session state for a token. |
| POST | `/api/walla-kelma/complete` | Completes a session (body includes `token`). |

All other GETs fall through to **static files** relative to the repo root.

### `quiz-feature/` — Modular front-end for quiz UI

| Path | Role |
|------|------|
| `pages/` | HTML + JS for **category selection**, **subcategory selection**, **quiz options**, and **quiz** play pages. |
| `components/` | Reusable UI pieces (loading, errors, question card, buttons, etc.). |
| `config/` | Category catalog, subcategory config, source maps (TS/JS). |
| `services/quiz-api.js` | Calls backend prepare / live-subcategory endpoints. |
| `state/quiz-session.js` | Client session state for the quiz flow. |
| `normalizers/` | Normalize API question shapes for the UI. |
| `styles/quiz-feature.css` | Feature-scoped CSS. |
| `types/` | Shared JS types/helpers for quiz data. |
| `utils/` | DOM, storage, validation helpers. |
| `ui/category-sections/` | Richer category UI (JSX/TSX components, runtime matchers, catalog wiring, optional TS types). |
| `data/` | Static JSON samples / caches used by the front-end tooling or dev (not a substitute for live backend preparation at runtime). |
| `scripts/` | Node scripts (e.g. generating fake banks for development). |

### `.vscode/`

Recommended editor extensions for contributors (optional).

---

## Architecture (mental model)

1. **Browser** loads static HTML/JS/CSS from the same origin as `server.py`.
2. **Quiz flow** calls `POST /api/quiz/prepare-match` with selected categories; **`backend/services/quiz_preparation.py`** pulls from **`source_clients`** via **`source_registry`**, applies quality / translation / normalization, returns a bank.
3. **Walla Kelma** uses create/session/complete endpoints and **`backend/services/walla_kelma_*`** with tokens; **`SEENJEEM_PUBLIC_BASE_URL`** ensures shared links and QR point at a **phone-reachable** origin.

---

## License

Add a `LICENSE` file if you want this repository to state terms explicitly.
