"""Purpose: host quiz and Walla Kelma routes with live-source-only runtime behavior."""

from http.server import SimpleHTTPRequestHandler

from backend.config import ROOT
from backend.services.category_mapping import (
    list_api_ready_ui_subcategory_ids,
    list_live_ui_subcategory_ids,
    list_walla_kelma_ready_ui_subcategory_ids,
)
from backend.services.quiz_preparation import prepare_match_question_bank
from backend.services.walla_kelma_service import (
    complete_walla_kelma,
    create_walla_kelma_session,
    get_walla_kelma_private_session,
)
from backend.utilities.http import (
    get_public_base_url,
    json_response,
    read_json_body,
)
from backend.utilities.debug import debug_log, debug_preview


class SeenJeemHandler(SimpleHTTPRequestHandler):
    """Serve static files plus the backend API routes used by the frontend."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/quiz/prepare-match":
            self.handle_prepare_match()
            return
        if self.path == "/api/walla-kelma/create":
            self.handle_create_walla_kelma()
            return
        if self.path == "/api/walla-kelma/complete":
            self.handle_complete_walla_kelma()
            return

        json_response(self, {"error": "Endpoint not found"}, status=404)

    def do_GET(self):
        if self.path == "/api/quiz/live-subcategories":
            self.handle_live_subcategories()
            return

        if self.path.startswith("/api/walla-kelma/session/"):
            self.handle_get_walla_kelma_session()
            return

        super().do_GET()

    def handle_prepare_match(self):
        payload = read_json_body(self)
        selected_items = payload.get("selectedSubcategories")
        debug_log("CATEGORY", "Selected from UI", debug_preview(selected_items, limit=10))

        if not isinstance(selected_items, list) or not selected_items:
            debug_log("REJECTED", "Reason", "selectedSubcategories is required")
            json_response(self, {"error": "selectedSubcategories is required"}, status=400)
            return

        try:
            question_bank, diagnostics = prepare_match_question_bank(selected_items)
            all_api_prepared = bool(diagnostics) and all(
                item.get("sourceMode") == "api" for item in diagnostics
            )
            response_payload = {
                "questionBank": question_bank,
                "preparedCount": len(question_bank),
                "diagnostics": diagnostics,
                "apiReady": all_api_prepared,
            }
            debug_log("FINAL", "Questions ready", debug_preview(question_bank, limit=5))
            debug_log("SERIALIZER", "Final payload", response_payload)
            json_response(
                self,
                response_payload,
            )
        except Exception as error:
            debug_log("API ERROR", "Request failed", str(error))
            json_response(
                self,
                {
                    "error": "تعذر تجهيز بنك الأسئلة من المصادر الحية",
                    "details": str(error),
                },
                status=500,
            )

    def handle_live_subcategories(self):
        quiz_ids = list_api_ready_ui_subcategory_ids()
        walla_ids = list_walla_kelma_ready_ui_subcategory_ids()
        subcategory_ids = list_live_ui_subcategory_ids()
        public_base_url = get_public_base_url(self)
        json_response(
            self,
            {
                "subcategoryIds": subcategory_ids,
                "quizSubcategoryIds": quiz_ids,
                "wallaKelmaSubcategoryIds": walla_ids,
                "count": len(subcategory_ids),
                "publicBaseUrl": public_base_url,
            },
        )

    def handle_create_walla_kelma(self):
        payload = read_json_body(self)
        selected_item = payload.get("selectedSubcategory") or {}
        difficulty = str(payload.get("difficulty") or "easy").strip().lower()
        debug_log("WALLA", "Create session request", {"selected_item": selected_item, "difficulty": difficulty})
        try:
            response_payload = create_walla_kelma_session(
                selected_item,
                difficulty,
                get_public_base_url(self),
            )
            debug_log("SERIALIZER", "Final payload", response_payload)
            json_response(self, response_payload)
        except Exception as error:
            debug_log("API ERROR", "Request failed", str(error))
            json_response(self, {"error": "تعذر إنشاء جلسة ولا كلمة", "details": str(error)}, status=400)

    def handle_get_walla_kelma_session(self):
        token = self.path.rsplit("/", 1)[-1].strip()
        debug_log("WALLA", "Get private session request", {"token": token})
        try:
            response_payload = get_walla_kelma_private_session(token)
            debug_log("SERIALIZER", "Final payload", response_payload)
            json_response(self, response_payload)
        except Exception as error:
            debug_log("API ERROR", "Request failed", str(error))
            json_response(self, {"error": "تعذر جلب جلسة ولا كلمة", "details": str(error)}, status=404)

    def handle_complete_walla_kelma(self):
        payload = read_json_body(self)
        token = str(payload.get("token") or "").strip()
        if not token:
            debug_log("REJECTED", "Reason", "token is required")
            json_response(self, {"error": "token is required"}, status=400)
            return
        try:
            response_payload = complete_walla_kelma(token, get_public_base_url(self))
            debug_log("SERIALIZER", "Final payload", response_payload)
            json_response(self, response_payload)
        except Exception as error:
            debug_log("API ERROR", "Request failed", str(error))
            json_response(self, {"error": "تعذر إنهاء جلسة ولا كلمة", "details": str(error)}, status=404)
