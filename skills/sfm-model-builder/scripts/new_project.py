"""Create a Level 2 project from the template: python new_project.py <folder> (the folder must be new or empty)."""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import records  # noqa: E402

TEMPLATE = Path(__file__).resolve().parents[3] / "template"

if __name__ == "__main__":
    t = Path(sys.argv[1]).expanduser().resolve()
    if t.exists() and any(t.iterdir()):
        sys.exit(f"{t} is not empty; choose a new folder")
    shutil.copytree(TEMPLATE, t, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    records.journey(t)
    print(t)
