"""The project's model page: SFM's own app.html, its data from SFM's modelpage functions on this project.
Run from the project root: python ui/server.py -> http://127.0.0.1:8900 (SFM_UI_PORT to change; only this machine).
The model is reloaded for every request, so a change in model/ shows on the next click."""
import importlib
import json
import math
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT, UI = Path(__file__).resolve().parents[1], Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT), str(UI)]
import records  # noqa: E402
from sfm import modelpage  # noqa: E402

SHOW_BUILD = os.environ.get("SHOW_BUILD_TAB", "1") != "0"
TABS = (["building"] if SHOW_BUILD else []) + ["baseline", "studio", "optimize"]
STATIC = {"/ct.css": ("ct.css", "text/css"), "/icon.svg": ("icon.svg", "image/svg+xml"),
          "/mermaid.min.js": ("mermaid.min.js", "text/javascript")}


def clean(x):
    """NaN and infinity are not JSON: None (as SFM's server does)."""
    if isinstance(x, float):
        return x if math.isfinite(x) else None
    if isinstance(x, dict):
        return {k: clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [clean(v) for v in x]
    return x


def project():
    import model.custom
    import model.model
    import model.project
    for m in (model.custom, model.model, model.project):    # pick up edits without a restart
        importlib.reload(m)
    return model.project.Project(ROOT)


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json", extra=()):
        data = body if isinstance(body, bytes) else json.dumps(clean(body), default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-cache")
        for k, v in extra:
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _route(self, method):
        path = self.path.split("?")[0]
        if method == "GET" and path == "/":
            return self._send(302, b"", "text/plain", [("Location", "/apps/project")])
        if method == "GET" and path == "/apps/project":
            html = (UI / "app.html").read_bytes().replace(b"</head>", b'<script src="/mermaid.min.js"></script></head>', 1)
            return self._send(200, html, "text/html; charset=utf-8")
        if method == "GET" and path in STATIC:
            name, ctype = STATIC[path]
            return self._send(200, (UI / name).read_bytes(), ctype)
        if path == "/api/me":
            return self._send(200, {"user": None, "auth": False, "setup": False})
        if not path.startswith("/api/apps/project"):
            return self._send(404, {"error": "not found"})
        rest = path[len("/api/apps/project"):].strip("/")
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}") if method == "POST" else None
        if rest == "":
            title = project().s.get("title") or "Simulation model"
            app = {"slug": "project", "title": title, "live": "local", "tabs": TABS, "project": True,
                   **({"building": "records"} if SHOW_BUILD else {})}
            return self._send(200, {"app": app, "use_case": {"id": "project", "title": title}})
        if rest == "building" and SHOW_BUILD:
            if method == "GET":
                return self._send(200, {"journey": records.journey(ROOT), "steps": records.steps(ROOT),
                                        "decisions": records.decisions(ROOT)})
            return self._send(200, records.decide(ROOT, int(body["step"]), body.get("decision", ""), body.get("text", ""),
                                                  body.get("who", ""), "tab"))
        if rest == "workbook.xlsx" and method == "GET":
            return self._send(200, modelpage.workbook_xlsx(project()),
                              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                              [("Content-Disposition", 'attachment; filename="scenario_workbook.xlsx"')])
        return self._send(200, modelpage.handle(project(), method, rest, body))

    def _safe(self, method):
        try:
            self._route(method)
        except (ValueError, KeyError) as e:
            self._send(400, {"error": str(e).strip("'\"")})
        except Exception as e:                              # the page shows the reason in the tab
            self._send(500, {"error": f"{type(e).__name__}: {e}"})

    def do_GET(self):
        self._safe("GET")

    def do_POST(self):
        self._safe("POST")


if __name__ == "__main__":
    port = int(os.environ.get("SFM_UI_PORT", "8900"))
    print(f"Model page on http://127.0.0.1:{port}", flush=True)
    ThreadingHTTPServer((os.environ.get("SFM_UI_HOST", "127.0.0.1"), port), H).serve_forever()
