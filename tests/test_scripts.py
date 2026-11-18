import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
S = ROOT / "skills" / "sfm-model-builder" / "scripts"
SAMPLE = ROOT / "samples" / "nps"


def run(*a, cwd=None):
    return subprocess.run([sys.executable, *map(str, a)], capture_output=True, text=True, cwd=cwd)


def _export(tmp_path):
    s = json.loads((SAMPLE / "model" / "session.json").read_text())
    x = {"sfm_version": "1.0.0", "use_case": "uc1", "title": s.get("title"), "tables": ["seg", "obs"], "session": s}
    (tmp_path / "x.json").write_text(json.dumps(x))
    return tmp_path / "x.json"


def test_new_project_copies_the_template_and_refuses_a_full_folder(tmp_path):
    p = tmp_path / "claims-model"
    assert run(S / "new_project.py", p).returncode == 0
    assert (p / "model" / "model.py").exists() and (p / "ui" / "server.py").exists() and (p / "build" / "journey.json").exists()
    out = run(S / "new_project.py", p)
    assert out.returncode != 0 and "not empty" in out.stderr


def test_export_with_its_data_makes_a_working_project(tmp_path):
    p = tmp_path / "proj"
    run(S / "new_project.py", p)
    r = json.loads(run(S / "export.py", p, _export(tmp_path), "--data", SAMPLE / "data" / "seg.csv", SAMPLE / "data" / "obs.csv").stdout)
    assert r["ok"] and r["missing"] == []
    assert json.loads((p / "build" / "journey.json").read_text())["use_case"] == "uc1"
    assert json.loads(run(S / "check.py", p).stdout)["ok"]


def test_export_without_a_table_says_which(tmp_path):
    p = tmp_path / "proj"
    run(S / "new_project.py", p)
    r = json.loads(run(S / "export.py", p, _export(tmp_path), "--data", SAMPLE / "data" / "seg.csv").stdout)
    assert r["ok"] is False and r["missing"] == ["obs"]


def test_compile_after_editing_the_process(tmp_path):
    p = tmp_path / "proj"
    run(S / "new_project.py", p)
    shutil.copytree(SAMPLE, p, dirs_exist_ok=True)
    before = json.loads((p / "model" / "session.json").read_text())["spec"]["levers"]
    out = run(S / "compile.py", p)
    r = json.loads(out.stdout.strip().splitlines()[-1])
    assert r["ok"], out.stdout + out.stderr
    assert json.loads((p / "model" / "session.json").read_text())["spec"]["levers"].keys() == before.keys()
    assert json.loads(run(S / "check.py", p).stdout)["ok"]


def test_compile_refuses_a_broken_process(tmp_path):
    p = tmp_path / "proj"
    run(S / "new_project.py", p)
    shutil.copytree(SAMPLE, p, dirs_exist_ok=True)
    saved = (p / "model" / "session.json").read_text()
    ps = json.loads((p / "model" / "procspec.json").read_text())
    ps["fact_table"] = "no_such_table"
    (p / "model" / "procspec.json").write_text(json.dumps(ps))
    out = run(S / "compile.py", p)
    assert out.returncode != 0 and json.loads(out.stdout.strip().splitlines()[-1])["ok"] is False
    assert (p / "model" / "session.json").read_text() == saved          # nothing saved


def test_check_reports_failures(tmp_path):
    p = tmp_path / "proj"
    run(S / "new_project.py", p)
    shutil.copytree(SAMPLE, p, dirs_exist_ok=True)
    (p / "model" / "custom.py").write_text("def adjust(spec):\n    raise RuntimeError('broken')\n")
    r = json.loads(run(S / "check.py", p).stdout)
    assert r["ok"] is False and r["failed"] >= 1


def test_template_assets_are_in_sync():
    assert run(ROOT / "scripts" / "sync_template.py", "--check").returncode == 0


def test_export_with_the_data_already_in_the_project(tmp_path):
    """The skill copies the data at step 2 and passes the same files at step 5."""
    p = tmp_path / "proj"
    run(S / "new_project.py", p)
    (p / "data").mkdir(exist_ok=True)
    for n in ("seg", "obs"):
        shutil.copy2(SAMPLE / "data" / f"{n}.csv", p / "data" / f"{n}.csv")
    out = run(S / "export.py", p, _export(tmp_path), "--data", p / "data" / "seg.csv", p / "data" / "obs.csv")
    assert out.returncode == 0, out.stderr
    assert json.loads(out.stdout)["ok"]


def test_export_of_an_error_says_so(tmp_path):
    p = tmp_path / "proj"
    run(S / "new_project.py", p)
    (tmp_path / "x.json").write_text(json.dumps({"error": "409: Level 2 needs a process-specification model"}))
    out = run(S / "export.py", p, tmp_path / "x.json")
    r = json.loads(out.stdout)
    assert r["ok"] is False and "process-specification" in r["note"] and not (p / "model" / "session.json").exists()


def test_a_parquet_table_counts_as_present(tmp_path):
    import pandas as pd
    p = tmp_path / "proj"
    run(S / "new_project.py", p)
    (p / "data").mkdir(exist_ok=True)
    pd.read_csv(SAMPLE / "data" / "obs.csv").to_parquet(p / "data" / "obs.parquet")
    r = json.loads(run(S / "export.py", p, _export(tmp_path), "--data", SAMPLE / "data" / "seg.csv").stdout)
    assert r["ok"] and r["missing"] == []
    assert json.loads(run(S / "check.py", p).stdout)["ok"]
