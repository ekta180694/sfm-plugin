"""The journey's records in a project's build/ folder (plugin spec §4): journey.json, steps/<n>-<name>.json and the
append-only decisions.json. Used by step.py, decide.py and the project's server. Standard library only."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

STEPS = ["setup", "inputs", "business", "data", "core_model", "process", "build", "ui"]
CHOICES = ("approve", "feedback", "back")


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _write(p: Path, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=1))
    os.replace(tmp, p)                         # a reader sees the old file or the new one, never half


def journey(root) -> dict:
    p = Path(root) / "build" / "journey.json"
    if not p.exists():
        _write(p, {"level": None, "current": 1, "status": {s: "to do" for s in STEPS}, "use_case": None, "approver": None})
    return json.loads(p.read_text())


def save_journey(root, j):
    _write(Path(root) / "build" / "journey.json", j)


def write_step(root, n: int, record: dict) -> Path:
    name = STEPS[n - 1]
    p = Path(root) / "build" / "steps" / f"{n}-{name}.json"
    _write(p, {"step": n, "name": name, "at": _now(), **record})
    j = journey(root)
    j["status"][name], j["current"] = "waiting", n
    save_journey(root, j)
    return p


def steps(root) -> list[dict]:
    d = Path(root) / "build" / "steps"
    return [json.loads(p.read_text()) for p in sorted(d.glob("*.json"), key=lambda p: int(p.name.split("-")[0]))] if d.exists() else []


def decisions(root) -> list[dict]:
    p = Path(root) / "build" / "decisions.json"
    if not p.exists():
        return []
    try:
        xs = json.loads(p.read_text())
    except ValueError as e:
        raise ValueError(f"build/decisions.json is not valid JSON ({e}); fix or restore it, nothing was changed") from None
    for i, x in enumerate(xs, 1):
        if not isinstance(x, dict) or x.get("decision") not in CHOICES or not isinstance(x.get("step"), int):
            raise ValueError(f"build/decisions.json line {i}: {json.dumps(x)[:120]} is not a decision "
                             f"(a step and approve, feedback or back)")
    return xs


def latest(root, step: int) -> dict | None:
    return next((x for x in reversed(decisions(root)) if x["step"] == step), None)


def decide(root, step: int, decision: str, text: str = "", who: str = "", source: str = "chat") -> dict:
    if decision not in CHOICES:
        raise ValueError(f"a decision is approve, feedback or back, not {decision!r}")
    xs = decisions(root)
    x = {"step": int(step), "decision": decision, "text": text, "who": who, "at": _now(), "source": source}
    _write(Path(root) / "build" / "decisions.json", xs + [x])
    j = journey(root)
    name = STEPS[step - 1]
    if decision == "approve":
        j["status"][name], j["current"] = "approved", min(step + 1, len(STEPS))
    elif decision == "feedback":
        j["status"][name] = "redo"
    else:
        for s in STEPS[step - 1:]:
            if j["status"][s] != "to do":
                j["status"][s] = "redo"
        j["status"][name], j["current"] = "redo", step
    save_journey(root, j)
    return x
