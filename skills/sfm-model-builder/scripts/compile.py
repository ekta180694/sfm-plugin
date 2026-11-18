"""Rebuild the model after editing model/procspec.json: SFM's own process and build steps on this project.
python compile.py <project>  ->  progress lines, then {"ok", "errors"}"""
import json
import sys
from pathlib import Path

if __name__ == "__main__":
    root = Path(sys.argv[1]).resolve()
    sys.path.insert(0, str(root))
    from model.project import Project
    p = Project(root)
    p.s["procspec"] = json.loads((root / "model" / "procspec.json").read_text())
    try:
        p.s.setdefault("records", {})["process"] = p._process_spec()
        p.s["records"]["build"] = p._build_spec()
    except Exception as e:                                 # the process does not fit the data: nothing is saved
        print(json.dumps({"ok": False, "errors": [f"{type(e).__name__}: {e}"[:600]]}))
        sys.exit(1)
    p.s["spec"]["status"] = "published"
    p.save()
    print(json.dumps({"ok": "error" not in p.s["records"]["build"], "errors": []}))
