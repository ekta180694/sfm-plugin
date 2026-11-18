# SFM plugin

Build a simulation model with a UI, step by step, in Claude Code or GitHub Copilot. The design is in the SFM repository:
`docs/SFM_Plugin_Design.md`.

- **Level 1: SFM as it is.** The assistant takes SFM (deployed, or started on your machine) through its steps with you,
  using SFM's MCP tools. You approve every step; the result is a Simulation App on SFM. Later changes are limited to what
  SFM allows.
- **Level 2: your own project.** The same journey ends in a project folder you own: the model built by SFM, its data, the
  same model page, and tests. You (or your assistant) can then change anything: the process, code rules, or the engine
  itself through `simulate()`. It runs and is hosted on its own, like Control Tower.

Both levels show **the same model page** (SFM's own); its first tab, Building Model, shows how the model was built.
The model page covers process-specification models (SFM's main model type) for now.

## Install

- **Claude Code:** `/plugin marketplace add ekta180694/sfm-plugin`, then `/plugin install sfm@sfm-plugins`, then
  `/sfm:new-model`. While the repository is private, this works for anyone whose git can read it.
- **GitHub Copilot (VS Code, agent mode):** follow `copilot/INSTALL.md`.

The first run guides you through setup: Python 3.12, the SFM environment (`~/.sfm/venv`, about 630 MB), and sign-in.

## What is here

| Path | What it is |
|---|---|
| `skills/sfm-model-builder/` | The skill: the journey (`SKILL.md`), the method (`method/`), the scripts (`scripts/`) |
| `template/` | The Level 2 project: `model/`, `data/`, `ui/` (SFM's model page), `build/`, `tests/`, hosting files |
| `commands/`, `.claude-plugin/`, `.mcp.json` | The Claude Code plugin |
| `copilot/` | The same for GitHub Copilot |
| `samples/nps/` | A small sample model used by the tests |
| `scripts/` | `make_sample.py`, `sync_template.py` (keeps the page equal to SFM's) |

## Tests

With an environment that has SFM installed: `python -m pytest -q tests`. The page check: `node tests/ui_check.mjs <url>`.
