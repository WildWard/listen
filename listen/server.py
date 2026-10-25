"""Local review server. Only listens on 127.0.0.1, so nothing is reachable from the network."""
import json
import mimetypes
import threading
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from . import report
from .engine import Survey

UI = Path(__file__).parent / "ui" / "index.html"


class App:
    """Holds the open survey and the state of a scan running in the background."""

    def __init__(self, survey: Survey | None = None):
        self.survey = survey
        self.state = "ready" if survey and survey.passes else "idle"
        self.log: list[str] = []
        self.lock = threading.Lock()

    def progress(self, msg: str) -> None:
        with self.lock:
            self.log = (self.log + [msg])[-50:]

    def open(self, folder: str, te: int, rescan: bool) -> dict:
        path = Path(folder).expanduser()
        if not path.is_dir():
            return {"error": f"Folder not found: {folder}"}
        if self.state == "scanning":
            return {"error": "A scan is already running."}
        survey = Survey(path, te)
        if survey.passes and not rescan:
            self.survey, self.state, self.log = survey, "ready", [f"Opened saved results for {path}"]
            return {"ok": True}
        self.survey, self.state, self.log = survey, "scanning", [f"Scanning {path}"]

        def run():
            try:
                survey.skipped = []
                survey.scan(progress=self.progress)
                self.state = "ready"
            except Exception as e:  # show the problem in the browser instead of dying silently
                self.progress(f"Scan failed: {e}")
                traceback.print_exc()
                self.state = "error"

        threading.Thread(target=run, daemon=True).start()
        return {"ok": True}

    def learn_reference(self, folder: str, te: int) -> dict:
        if not self.survey or self.state != "ready":
            return {"error": "Open a survey first."}
        path = Path(folder).expanduser() if folder else None
        if path is not None and not path.is_dir():
            return {"error": f"Folder not found: {folder}"}
        survey = self.survey
        self.state, self.log = "scanning", [f"Learning species from {path}" if path else "Removing reference library"]

        def run():
            try:
                survey.set_reference(path, te, progress=self.progress)
                self.state = "ready"
            except Exception as e:
                self.progress(f"Reference library failed: {e}")
                traceback.print_exc()
                self.state = "ready"  # the survey itself is still fine

        threading.Thread(target=run, daemon=True).start()
        return {"ok": True}

    def status(self) -> dict:
        with self.lock:
            return {"state": self.state, "log": self.log[-8:],
                    "folder": str(self.survey.folder) if self.survey else None}


def make_handler(app: App):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # keep the console quiet
            pass

        def _send(self, body: bytes, ctype: str, code: int = 200):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, obj, code: int = 200):
            self._send(json.dumps(obj).encode("utf8"), "application/json", code)

        def _ready(self) -> bool:
            if app.state != "ready" or not app.survey:
                self._json({"error": "No survey is ready yet.", "status": app.status()}, 409)
                return False
            return True

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                return self._send(UI.read_bytes(), "text/html; charset=utf-8")
            if self.path == "/i18n.js":
                return self._send((UI.parent / "i18n.js").read_bytes(), "text/javascript; charset=utf-8")
            if self.path == "/api/status":
                return self._json(app.status())
            if self.path == "/api/survey":
                return self._ready() and self._json(app.survey.summary())
            if self.path.startswith("/media/") and app.survey:
                name = Path(self.path[len("/media/"):]).name  # no directory tricks
                f = app.survey.media / name
                if f.exists():
                    return self._send(f.read_bytes(), mimetypes.guess_type(f.name)[0] or "application/octet-stream")
            return self._json({"error": "not found"}, 404)

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(n) or b"{}")
            if self.path == "/api/open":
                res = app.open(str(body.get("folder", "")), int(body.get("te") or 1), bool(body.get("rescan")))
                return self._json(res, 400 if "error" in res else 200)
            if self.path == "/api/reference":
                res = app.learn_reference(str(body.get("folder") or ""), int(body.get("te") or 1))
                return self._json(res, 400 if "error" in res else 200)
            if self.path == "/api/label":
                if not self._ready():
                    return
                ids = [int(i) for i in body.get("passes", []) if 0 <= int(i) < len(app.survey.passes)]
                app.survey.label(ids, body.get("label"))
                return self._json(app.survey.summary())
            if self.path == "/api/export":
                return self._ready() and self._json(report.export(app.survey))
            return self._json({"error": "not found"}, 404)

    return Handler


def serve(app: App, port: int = 8790) -> ThreadingHTTPServer:
    return ThreadingHTTPServer(("127.0.0.1", port), make_handler(app))
