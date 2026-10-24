"""WildWard Listen: python run.py [folder of recordings] [--te 16] [--port 8790]

With a folder, it opens (or scans) that survey. Without one, pick a folder in the browser.
Results are saved in <folder>/.wildward/ so closing the app never loses work.
"""
import argparse
import webbrowser
from pathlib import Path

from listen.engine import Survey
from listen.server import App, serve


def main() -> None:
    ap = argparse.ArgumentParser(description="Offline bat call review")
    ap.add_argument("folder", type=Path, nargs="?")
    ap.add_argument("--te", type=int, default=1, help="time-expansion factor if files are stored slowed down (often 10 or 16)")
    ap.add_argument("--port", type=int, default=8790)
    ap.add_argument("--rescan", action="store_true", help="ignore saved results and scan again")
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args()

    app = App()
    if a.folder:
        res = app.open(str(a.folder), a.te, a.rescan)
        if "error" in res:
            print(res["error"])
    server = serve(app, a.port)
    url = f"http://127.0.0.1:{a.port}"
    print(f"WildWard Listen is running at {url}  (Ctrl+C to stop)")
    if not a.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
