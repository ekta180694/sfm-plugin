"""Build the sample project model (samples/nps/) from SFM's offline test model, through SFM's own steps (no LLM):
python scripts/make_sample.py samples/nps"""
import json
import os
import sys
import tempfile
from pathlib import Path

SFM = Path(os.environ.get("SFM_REPO", "/data/projects/ekta/Simulation AI"))
sys.path[:0] = [str(SFM / "src"), str(SFM / "tests")]
os.environ["SFM_NO_LLM"] = "1"

from sfm import apps, session as S  # noqa: E402
from test_composition import DOC_KPIS, SPEC, tables  # noqa: E402

if __name__ == "__main__":
    out = Path(sys.argv[1]).resolve()
    (out / "model").mkdir(parents=True, exist_ok=True)
    (out / "data").mkdir(exist_ok=True)
    S.RUNS = Path(tempfile.mkdtemp())
    for n, df in tables().items():
        df.to_csv(out / "data" / f"{n}.csv", index=False)
    ses = S.Session.new()
    ses.s["inputs"]["data"] = [str(out / "data" / "seg.csv"), str(out / "data" / "obs.csv")]
    ses.s["inputs"]["shape"], ses.s["procspec"] = "spec", SPEC
    ses.s["profile"] = {"objective": "nps", "process_steps": [], "kpis": DOC_KPIS, "drivers": []}
    for st in ("data", "process", "build"):
        ses._run(st)
    ses.s["spec"]["status"], ses.s["stage"], ses.s["title"] = "published", "ready", "NPS sample"
    x = apps.export(ses)
    (out / "model" / "session.json").write_text(json.dumps(x["session"], indent=1, default=str))
    (out / "model" / "procspec.json").write_text(json.dumps(x["session"]["procspec"], indent=1))
    print(out, x["tables"])
