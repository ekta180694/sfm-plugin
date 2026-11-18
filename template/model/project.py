"""The project as SFM's model page sees a use case: the exported model record (model/session.json), the data tables
(data/) and the engine hook (model.simulate). It inherits SFM's process-specification steps, so compile.py can rebuild."""
import json
import os
from pathlib import Path

from sfm.canonical import load_tables
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
        files = sorted(p for p in (self.root / "data").iterdir() if p.suffix in (".csv", ".parquet"))
        return load_tables([str(p) for p in files])

    def save(self):
        tmp = self.file.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.s, indent=1, default=str))
        os.replace(tmp, self.file)

    def conversations(self):
        return []

    def progress(self, text):
        print(text, flush=True)
