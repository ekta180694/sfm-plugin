import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "skills" / "sfm-model-builder"


def test_manifests_are_valid_json_with_names():
    p = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
    m = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
    mcp = json.loads((ROOT / ".mcp.json").read_text())
    assert p["name"] == "sfm" and m["plugins"][0]["name"] == "sfm" and "sfm" in mcp["mcpServers"]
    assert json.loads((ROOT / "copilot" / "mcp.json").read_text())["servers"]["sfm"]


def test_skill_has_frontmatter_and_every_referenced_file_exists():
    text = (SKILL / "SKILL.md").read_text()
    front = re.match(r"---\nname: (.+)\ndescription: (.+?)\n---\n", text, re.S)
    assert front and front.group(1).strip() == "sfm-model-builder" and len(front.group(2)) > 50
    for ref in re.findall(r"`((?:scripts|method)/[\w./-]+)`", text):
        assert (SKILL / ref).exists(), ref


def test_skill_covers_every_step_and_the_three_choices():
    text = (SKILL / "SKILL.md").read_text()
    for s in ["Step 0", *[f"Step {n} of 8" for n in range(1, 9)], "Approve", "Give feedback", "Go back", "sfm login",
              "never", "sfm_connect", "sfm_export", "compile.py", "check.py"]:
        assert s in text, s


def test_commands_point_to_the_skill():
    for f in ["commands/new-model.md", "commands/continue.md", "copilot/prompts/sfm-new-model.prompt.md",
              "copilot/prompts/sfm-continue.prompt.md"]:
        assert "sfm-model-builder" in (ROOT / f).read_text(), f
