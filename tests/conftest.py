import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]


@pytest.fixture
def project(tmp_path):
    p = tmp_path / "proj"
    shutil.copytree(ROOT / "template", p, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    shutil.copytree(ROOT / "samples" / "nps", p, dirs_exist_ok=True)
    return p
