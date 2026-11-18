# Your simulation model

A project made with the SFM plugin. The model page is SFM's own model page; its numbers come from `model/model.py`.

| Folder | What is in it |
|---|---|
| `model/` | `session.json` (the model record from SFM), `procspec.json` (the process, editable), `model.py` (`simulate()`, the engine hook), `custom.py` (your code rules), `project.py` |
| `data/` | The data tables, named as in SFM |
| `ui/` | The model page and its small server |
| `build/` | How the model was built: steps and decisions (the Building Model tab) |
| `tests/` | Checks every change must pass; `tests/expectations.json` holds the approved effect directions |

- **Run the page:** `./run.sh` (Windows: `./run.ps1`), then open http://127.0.0.1:8900
- **Run the checks:** `python -m pytest -q tests`
- **Change the model:** the process in `model/procspec.json`, then rebuild with the plugin's `compile.py`; code rules in
  `model/custom.py`; or your own logic in `simulate()` in `model/model.py`. Keep `simulate()`'s result form (the same as
  SFM's engine) and the checks passing.
- **Host it on its own:** build the `Dockerfile` (see its first lines). `SHOW_BUILD_TAB=0` hides the build history.
