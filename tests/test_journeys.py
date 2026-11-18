"""Level 2 end to end (plugin spec §8): a published SFM model becomes a project with the same page numbers, and a
change in the project's hook changes them."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
S = ROOT / "skills" / "sfm-model-builder" / "scripts"
SFM = Path("/data/projects/ekta/Simulation AI")
sys.path[:0] = [str(SFM / "src"), str(SFM / "tests")]


def run(*a, cwd=None):
    out = subprocess.run([sys.executable, *map(str, a)], capture_output=True, text=True, cwd=cwd)
    assert out.returncode == 0, out.stderr
    return out


def test_a_published_model_becomes_a_project_with_the_same_numbers(tmp_path, monkeypatch):
    from sfm import apps, modelpage
    from test_watch import _live_app
    (tmp_path / "sfm").mkdir()
    ses = _live_app(tmp_path / "sfm", monkeypatch)
    (tmp_path / "x.json").write_text(json.dumps(apps.export(ses), default=str))
    p = tmp_path / "proj"
    run(S / "new_project.py", p)
    for n in (1, 2, 3, 4):
        (p / "r.json").write_text(json.dumps({"title": f"step {n}", "summary": "ok"}))
        run(S / "step.py", p, n, p / "r.json")
        run(S / "decide.py", p, n, "approve", "--who", "test")
    r = json.loads(run(S / "export.py", p, tmp_path / "x.json", "--data", *ses.s["inputs"]["data"]).stdout)
    assert r["ok"], r
    assert json.loads(run(S / "check.py", p).stdout)["ok"]
    sys.path.insert(0, str(p))
    for m in [m for m in sys.modules if m == "model" or m.startswith("model.")]:
        del sys.modules[m]
    from model.project import Project
    st = modelpage.handle(ses, "GET", "studio")
    body = {"shift": {st["levers"][0]["column"]: st["levers"][0]["hi"]}, "reps": 50}
    a, b = modelpage.handle(ses, "POST", "run", body), modelpage.handle(Project(p), "POST", "run", body)
    for k in a["kpis"]:
        assert b["kpis"][k]["delta"] == pytest.approx(a["kpis"][k]["delta"]), k
    proj = Project(p)
    base = proj.simulate

    def shifted(spec, scen, reps, seed):                    # a deep change: Roko's own logic on top of SFM's engine
        tr = base(spec, scen, reps, seed)
        return {k: (v if k == "_theta" else v + 1.0) for k, v in tr.items()}
    proj.simulate = shifted
    c = modelpage.handle(proj, "POST", "run", body)
    assert any(c["kpis"][k]["scenario"] != pytest.approx(b["kpis"][k]["scenario"]) for k in b["kpis"])
    assert json.loads((p / "build" / "journey.json").read_text())["current"] == 5
