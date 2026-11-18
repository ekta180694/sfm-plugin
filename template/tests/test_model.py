"""Every project's model must pass these (plugin spec §5)."""
import json
from pathlib import Path

import numpy as np
from sfm import modelpage
from sfm.spec import ModelSpec, Scenario

from model.project import Project

ROOT = Path(__file__).parents[1]


def spec():
    return ModelSpec.model_validate(Project(ROOT).s["spec"])


def test_the_hook_returns_every_stock_and_flow():
    ms = spec()
    tr = Project(ROOT).simulate(ms, Scenario(name="baseline"), 5, 0)
    names = set(ms.stocks) | {f.name for f in ms.flows}
    assert names <= set(tr), sorted(names - set(tr))
    assert all(np.asarray(tr[n]).shape[0] == 5 for n in names)


def test_balances_hold_and_stocks_never_go_negative():
    ms, tr = spec(), Project(ROOT).simulate(spec(), Scenario(name="baseline"), 20, 0)
    for k in ms.stocks:                                   # x_{t+1} - x_t = inflows - outflows, and never below zero
        lvl = np.concatenate([tr[k], tr[k + "@end"][:, None]], axis=1)
        net = sum((tr[f.name] for f in ms.flows if f.to == k), 0) - sum((tr[f.name] for f in ms.flows if f.src == k), 0)
        assert np.abs(np.diff(lvl, axis=1) - net).max() < 1e-6, f"stock {k}: balance off"
        assert lvl.min() > -1e-6, f"stock {k}: went negative"


def test_no_change_means_no_difference():
    r = modelpage.handle(Project(ROOT), "POST", "run", {"shift": {}, "reps": 20})
    assert all(abs(v["delta"]) < 1e-9 for v in r["kpis"].values())


def test_the_model_page_data_builds():
    p = Project(ROOT)
    for route in ("baseline", "studio", "workbook", "scenarios"):
        assert modelpage.handle(p, "GET", route), route


def test_approved_effect_directions():
    p = Project(ROOT)
    cols = {lv["column"]: lv for lv in modelpage.handle(p, "GET", "studio")["levers"]}
    for e in json.loads((ROOT / "tests" / "expectations.json").read_text()):
        r = modelpage.handle(p, "POST", "run", {"shift": {e["lever"]: cols[e["lever"]]["hi"]}, "reps": 50})
        assert e["direction"] * r["kpis"][e["kpi"]]["delta"] > 0, e["why"]
