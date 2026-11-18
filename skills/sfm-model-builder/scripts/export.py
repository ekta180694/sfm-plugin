"""Put SFM's exported model into a project:
python export.py <project> <export.json from sfm_export> --data <file> [<file> ...]
The files are the user's own copies of the tables SFM used, named as in the export (file name without extension)."""
import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import records  # noqa: E402

if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("project"), a.add_argument("export"), a.add_argument("--data", nargs="*", default=[])
    x = a.parse_args()
    root, ex = Path(x.project), json.loads(Path(x.export).read_text())
    (root / "model").mkdir(exist_ok=True)
    (root / "data").mkdir(exist_ok=True)
    for f in map(Path, x.data):
        shutil.copy2(f, root / "data" / f.name)
    have = {p.stem for p in (root / "data").iterdir() if p.suffix in (".csv", ".parquet")}
    missing = [t for t in ex["tables"] if t not in have]
    (root / "model" / "session.json").write_text(json.dumps(ex["session"], indent=1, default=str))
    (root / "model" / "procspec.json").write_text(json.dumps(ex["session"]["procspec"], indent=1))
    j = records.journey(root)
    j["use_case"] = ex["use_case"]
    records.save_journey(root, j)
    note = (f"{ex['title']}: SFM's model is in model/, the data in data/" if not missing
            else f"copy these tables into data/ with these names: {', '.join(missing)}")
    print(json.dumps({"ok": not missing, "note": note, "missing": missing}))
