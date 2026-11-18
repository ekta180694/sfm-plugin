import json
import subprocess
import sys
from pathlib import Path

SFM = Path("/data/projects/ekta/Simulation AI")
sys.path.insert(0, str(SFM / "tests"))


def _pytest(p):
    return subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"], cwd=p,
                          capture_output=True, text=True)


def _project_class(p):
    sys.path.insert(0, str(p))
    for m in [m for m in sys.modules if m == "model" or m.startswith("model.")]:
        del sys.modules[m]                                 # each test's own copy of the template
    from model.project import Project
    return Project


def test_the_sample_project_passes_its_tests(project):
    out = _pytest(project)
    assert out.returncode == 0, out.stdout[-2000:]


def test_the_project_page_equals_sfms_page_for_the_same_model(project, tmp_path, monkeypatch):
    """Same model record and data: the Baseline and a Studio run are identical in SFM and in the project."""
    from sfm import modelpage
    from test_watch import _live_app
    ses = _live_app(tmp_path, monkeypatch)
    p = _project_class(project)(project)
    a, b = modelpage.handle(ses, "GET", "baseline"), modelpage.handle(p, "GET", "baseline")
    assert json.dumps(a, sort_keys=True, default=str) == json.dumps(b, sort_keys=True, default=str)
    st = modelpage.handle(ses, "GET", "studio")
    body = {"shift": {st["levers"][0]["column"]: st["levers"][0]["hi"]}, "reps": 50}
    ra, rb = modelpage.handle(ses, "POST", "run", body), modelpage.handle(p, "POST", "run", body)
    assert json.dumps(ra["kpis"], sort_keys=True) == json.dumps(rb["kpis"], sort_keys=True)


def test_a_broken_hook_fails_the_projects_tests(project):
    (project / "model" / "custom.py").write_text("def adjust(spec):\n    raise RuntimeError('broken on purpose')\n")
    assert _pytest(project).returncode != 0


def test_a_wrong_effect_direction_fails(project):
    from sfm import modelpage
    p = _project_class(project)(project)
    st = modelpage.handle(p, "GET", "studio")
    lv, k = st["levers"][0], st["kpis"][0]["name"]
    r = modelpage.handle(p, "POST", "run", {"shift": {lv["column"]: lv["hi"]}, "reps": 50})
    wrong = -1 if r["kpis"][k]["delta"] > 0 else 1
    (project / "tests" / "expectations.json").write_text(
        json.dumps([{"lever": lv["column"], "kpi": k, "direction": wrong, "why": "on purpose"}]))
    assert _pytest(project).returncode != 0
