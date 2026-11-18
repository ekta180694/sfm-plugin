"""Keep the template's copies equal to their sources: python scripts/sync_template.py [--check]"""
import filecmp
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SFM = Path(os.environ.get("SFM_REPO", "/data/projects/ekta/Simulation AI"))
PAIRS = [(SFM / "src/sfm/static" / n, ROOT / "template/ui" / n) for n in ("app.html", "ct.css", "icon.svg")] + [
    (SFM / "docs/tools/node_modules/mermaid/dist/mermaid.min.js", ROOT / "template/ui/mermaid.min.js"),
    (ROOT / "skills/sfm-model-builder/scripts/records.py", ROOT / "template/ui/records.py")]

if __name__ == "__main__":
    differ = [str(d) for s, d in PAIRS if s.exists() and not (d.exists() and filecmp.cmp(s, d, shallow=False))]
    if "--check" in sys.argv:
        sys.exit(f"out of sync: {differ}" if differ else 0)
    for s, d in PAIRS:
        shutil.copy2(s, d)
    print("synced", len(PAIRS))
