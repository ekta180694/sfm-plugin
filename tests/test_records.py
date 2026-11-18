import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "skills" / "sfm-model-builder" / "scripts"))
import records as R  # noqa: E402


def test_journey_starts_at_step_one(tmp_path):
    j = R.journey(tmp_path)
    assert j["current"] == 1 and set(j["status"].values()) == {"to do"} and (tmp_path / "build" / "journey.json").exists()


def test_write_step_then_approve_moves_on(tmp_path):
    R.write_step(tmp_path, 3, {"title": "Business", "summary": "Two KPIs", "diagrams": ["flowchart LR; a-->b"]})
    assert R.journey(tmp_path)["status"]["business"] == "waiting"
    R.decide(tmp_path, 3, "approve", who="Roko", source="tab")
    j = R.journey(tmp_path)
    assert j["status"]["business"] == "approved" and j["current"] == 4 and R.latest(tmp_path, 3)["source"] == "tab"


def test_back_marks_later_steps_to_redo(tmp_path):
    for n in (2, 3, 4):
        R.write_step(tmp_path, n, {"title": str(n), "summary": ""})
        R.decide(tmp_path, n, "approve")
    R.decide(tmp_path, 3, "back", text="KPI formula is wrong")
    j = R.journey(tmp_path)
    assert j["current"] == 3 and j["status"]["business"] == "redo" and j["status"]["data"] == "redo"
    assert j["status"]["inputs"] == "approved"


def test_decisions_are_only_appended(tmp_path):
    R.decide(tmp_path, 2, "feedback", text="add the claims table")
    R.decide(tmp_path, 2, "approve")
    assert [d["decision"] for d in R.decisions(tmp_path)] == ["feedback", "approve"]


def test_a_damaged_decision_file_names_the_line(tmp_path):
    R.decide(tmp_path, 2, "approve")
    f = tmp_path / "build" / "decisions.json"
    f.write_text(json.dumps(json.loads(f.read_text()) + [{"step": 3, "decision": "maybe"}]))
    with pytest.raises(ValueError, match="entry 2"):
        R.decisions(tmp_path)


def test_a_half_written_decision_file_is_refused(tmp_path):
    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "decisions.json").write_text('[{"step": 2, "decision": "appr')
    with pytest.raises(ValueError, match="decisions.json"):
        R.decisions(tmp_path)


def test_unknown_decision_is_refused(tmp_path):
    with pytest.raises(ValueError, match="approve, feedback or back"):
        R.decide(tmp_path, 2, "ok")


def _many(root, k):
    sys.path.insert(0, str(Path(__file__).parents[1] / "skills" / "sfm-model-builder" / "scripts"))
    import records
    for _ in range(k):
        records.decide(root, 2, "feedback", text="x")


def test_concurrent_decisions_are_all_kept(tmp_path):
    """A tab click and a chat decision at the same moment: both are kept (append-only)."""
    import multiprocessing as mp
    R.journey(tmp_path)
    ps = [mp.Process(target=_many, args=(tmp_path, 30)) for _ in range(2)]
    [p.start() for p in ps]
    [p.join() for p in ps]
    assert len(R.decisions(tmp_path)) == 60


@pytest.mark.parametrize("step", [0, 9, -1])
def test_a_step_outside_the_journey_is_refused_before_anything_is_written(tmp_path, step):
    with pytest.raises(ValueError, match="step"):
        R.decide(tmp_path, step, "approve")
    assert R.decisions(tmp_path) == []


def test_a_saved_decision_for_no_such_step_is_refused(tmp_path):
    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "decisions.json").write_text(json.dumps([{"step": 9, "decision": "approve"}]))
    with pytest.raises(ValueError, match="entry 1"):
        R.decisions(tmp_path)
