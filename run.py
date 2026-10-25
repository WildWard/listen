"""WildWard Listen: python run.py [folder of recordings] [--te 16] [--port 8790] [--app]

With a folder, it opens (or scans) that survey. Without one, pick a folder in the app.
--app opens Listen in its own desktop window (with folder pickers and drag and drop) instead of
the web browser. The installers' launchers use it.
Results are saved in <folder>/.wildward/ so closing the app never loses work.
"""
import argparse
import json
import sys
import threading
import webbrowser
from pathlib import Path

from listen.server import App, serve


class WindowApi:
    """Called from the page as window.pywebview.api.* when Listen runs in its own window."""

    def __init__(self):
        self._window = None   # underscore: pywebview must not expose the native window to the page

    def pick_folder(self, title: str = "Choose a folder"):
        import webview
        res = self._window.create_file_dialog(webview.FileDialog.FOLDER)
        return res[0] if res else None


def run_window(url: str, server) -> None:
    """A native desktop window around the local page (WebView2 on Windows, WebKit on macOS)."""
    import webview
    from webview.dom import DOMEventHandler

    api = WindowApi()
    window = webview.create_window("WildWard Listen", url, js_api=api, width=1280, height=860, min_size=(420, 520),
                                   background_color="#0a1510", text_select=True)
    api._window = window

    def on_drop(e):
        # a dropped folder opens as a survey (or library); a dropped recording opens its folder
        files = (e.get("dataTransfer") or {}).get("files") or []
        paths = [f.get("pywebviewFullPath") for f in files if f.get("pywebviewFullPath")]
        if paths:
            p = Path(paths[0])
            folder = p if p.is_dir() else p.parent
            window.evaluate_js(f"window.onDropFolder && onDropFolder({json.dumps(str(folder))})")

    def bind():
        noop = lambda e: None
        window.dom.document.events.dragenter += DOMEventHandler(noop, True, True)
        window.dom.document.events.dragover += DOMEventHandler(noop, True, True)
        window.dom.document.events.drop += DOMEventHandler(on_drop, True, True)

    window.events.loaded += bind
    icon = Path(__file__).parent / "listen" / "ui" / "icon.ico"
    webview.start(icon=str(icon) if icon.exists() else None)
    server.shutdown()   # window closed: stop the local server too


def quiet_console() -> None:
    """Started without a console (pythonw, the desktop shortcut): send output to a log file instead."""
    if sys.stdout is None or sys.stderr is None:
        log = open(Path.home() / ".wildward-listen.log", "a", encoding="utf8", buffering=1)
        sys.stdout = sys.stdout or log
        sys.stderr = sys.stderr or log


def main() -> None:
    ap = argparse.ArgumentParser(description="Offline bat call review")
    ap.add_argument("folder", type=Path, nargs="?")
    ap.add_argument("--te", type=int, default=1, help="time-expansion factor if files are stored slowed down (often 10 or 16)")
    ap.add_argument("--port", type=int, default=8790)
    ap.add_argument("--rescan", action="store_true", help="ignore saved results and scan again")
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--app", action="store_true", help="open in a desktop window instead of the browser")
    a = ap.parse_args()
    quiet_console()

    app = App()
    if a.folder:
        res = app.open(str(a.folder), a.te, a.rescan)
        if "error" in res:
            print(res["error"])
    try:
        server = serve(app, a.port)
    except OSError:   # port taken, e.g. Listen is already open: use any free one
        server = serve(app, 0)
    url = f"http://127.0.0.1:{server.server_address[1]}"
    if a.app:
        try:
            import webview  # noqa: F401
        except ImportError:
            print("Desktop window not available (pywebview missing), opening in the browser instead.")
            a.app = False
    if a.app:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        print(f"WildWard Listen is running in its own window ({url}). Close the window to stop.")
        run_window(url, server)
        return
    print(f"WildWard Listen is running at {url}  (Ctrl+C to stop)")
    if not a.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
