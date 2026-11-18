# The SFM plugin in GitHub Copilot (VS Code, agent mode)

1. Skill: copy `skills/sfm-model-builder` to `~/.copilot/skills/sfm-model-builder` (all projects) or to
   `.github/skills/sfm-model-builder` in one repository. If your Copilot does not list it under `/skills`, copy `SKILL.md`
   to `.github/instructions/sfm-model-builder.instructions.md` instead.
2. MCP: copy `copilot/mcp.json` to `.vscode/mcp.json` (or add its `servers` entry to your user settings) and start the
   `sfm` server from the MCP view.
3. Commands: copy `copilot/prompts/*.prompt.md` to `.github/prompts/`; then type `/sfm-new-model` in the chat.
4. The first run guides you through the rest (Python, the SFM environment, sign-in).
