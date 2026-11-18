# Release checklist

- [ ] `python scripts/sync_template.py --check` passes (the page and assets equal SFM's).
- [ ] `python -m pytest -q tests` passes.
- [ ] SFM's address and tag known; `SFM_SOURCE` documented in README, `setup.ps1` and the Dockerfile build command.
- [ ] One full journey in Claude Code (terminal): Level 1 and Level 2; one checkpoint approved in the chat and one in the tab.
- [ ] One full journey in GitHub Copilot (VS Code agent mode) following `copilot/INSTALL.md`.
- [ ] Windows: `setup.ps1`, `run.ps1`, the page opens.
- [ ] Plugin version bumped in `.claude-plugin/plugin.json`.
