import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

import pytest


@pytest.fixture
def ui(project):
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    proc = subprocess.Popen([sys.executable, "ui/server.py"], cwd=project, env={**os.environ, "SFM_UI_PORT": str(port)},
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    base = f"http://127.0.0.1:{port}"
    for _ in range(80):
        if proc.poll() is not None:                      # the server stopped: no point waiting
            break
        try:
            urllib.request.urlopen(base + "/api/me", timeout=2)
            break
        except (urllib.error.URLError, ConnectionError):
            time.sleep(0.25)
    else:
        proc.kill()
        raise AssertionError(proc.stderr.read().decode()[-1500:])
    yield base, project
    proc.terminate()
    proc.wait(5)


def call(base, path, body=None):
    req = urllib.request.Request(base + path, json.dumps(body).encode() if body is not None else None,
                                 {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
            return r.status, (json.loads(data) if "json" in r.headers.get("Content-Type", "") else data)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def test_the_page_is_sfms_page(ui):
    base, _ = ui
    code, html = call(base, "/apps/project")
    sfm = open("/data/projects/ekta/Simulation AI/src/sfm/static/app.html", "rb").read()
    assert code == 200 and html.replace(b'<script src="/mermaid.min.js"></script>', b"") == sfm


def test_app_tabs_and_data_routes(ui):
    base, _ = ui
    code, a = call(base, "/api/apps/project")
    assert code == 200 and a["app"]["tabs"] == ["building", "baseline", "studio", "optimize"] and a["app"]["project"]
    assert call(base, "/api/apps/project/baseline")[0] == 200
    code, st = call(base, "/api/apps/project/studio")
    lv = st["levers"][0]
    code, r = call(base, "/api/apps/project/run", {"shift": {lv["column"]: lv["hi"]}, "reps": 30})
    assert code == 200 and r["kpis"]


def test_bad_requests_are_400(ui):
    base, _ = ui
    code, r = call(base, "/api/apps/project/run", {"shift": {"no_such_lever": 1}})
    assert code == 400 and "unknown levers" in r["error"]
    assert call(base, "/api/apps/project/nothing")[0] == 400


def test_building_records_and_a_decision_from_the_tab(ui):
    base, p = ui
    sys.path.insert(0, str(p / "ui"))
    import records
    records.write_step(p, 2, {"title": "Inputs", "summary": "Two tables found", "diagrams": ["flowchart LR; data-->model"]})
    code, b = call(base, "/api/apps/project/building")
    assert code == 200 and b["steps"][0]["title"] == "Inputs" and b["journey"]["current"] == 2
    code, d = call(base, "/api/apps/project/building", {"step": 2, "decision": "approve"})
    assert code == 200 and d["source"] == "tab"
    assert call(base, "/api/apps/project/building", {"step": 2, "decision": "ok"})[0] == 400


def test_a_broken_hook_shows_its_reason(ui):
    base, p = ui
    (p / "model" / "custom.py").write_text("def adjust(spec):\n    raise RuntimeError('broken on purpose')\n")
    code, r = call(base, "/api/apps/project/baseline")
    assert code == 500 and "broken on purpose" in r["error"]


def test_a_post_from_another_website_is_refused(ui):
    """A page on another site cannot approve steps or change the model through the local server."""
    base, p = ui
    req = urllib.request.Request(base + "/api/apps/project/building", json.dumps({"step": 2, "decision": "approve"}).encode(),
                                 {"Content-Type": "application/json", "Origin": "https://evil.example"})
    with pytest.raises(urllib.error.HTTPError) as e:
        urllib.request.urlopen(req, timeout=30)
    assert e.value.code == 403
    req = urllib.request.Request(base + "/api/apps/project/building", json.dumps({"step": 2, "decision": "approve"}).encode(),
                                 {"Content-Type": "text/plain"})
    with pytest.raises(urllib.error.HTTPError) as e:
        urllib.request.urlopen(req, timeout=30)
    assert e.value.code == 415
    assert not (p / "build" / "decisions.json").exists()
