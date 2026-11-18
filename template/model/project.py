"""The project as SFM's model page sees a use case: the exported model record (model/session.json), the data tables
(data/) and the engine hook (model.simulate). It inherits SFM's process-specification steps, so compile.py can rebuild."""
import json
import os
from pathlib import Path

from sfm import fixes
from sfm.canonical import load_tables
from sfm.catalog import is_table
from sfm.session_spec import SpecStages

from . import model


class Project(SpecStages):
    def __init__(self, root):
        self.root = Path(root)
        self.file = self.root / "model" / "session.json"
        self.s = json.loads(self.file.read_text())
        self.id = "project"
        self.simulate = model.simulate

    def _spec_tables(self):
        """The tables as SFM reads them (files and folders of parts, by name), with the use case's approved transforms."""
        paths = sorted(str(p) for p in (self.root / "data").iterdir() if not p.name.startswith(".") and is_table(p))
        return fixes.apply(load_tables(paths), self.s.get("extensions"))

    def save(self):
        import tempfile
        fd, tmp = tempfile.mkstemp(dir=self.file.parent, suffix=".tmp")
        with os.fdopen(fd, "w") as f:
            f.write(json.dumps(self.s, indent=1, default=str))
        os.replace(tmp, self.file)

    def conversations(self):
        return []

    def progress(self, text):
        print(text, flush=True)
