# The modelling method (plain words)

These are SFM's own rules. Follow them in both levels.

## The model form and its shapes

SFM builds most businesses from a short **model form**: the shape of the business and which data columns fill each slot.
Choose the shape from the process, the data and the KPI, never from the department's name.

| Shape | Use it when | Example |
|---|---|---|
| ratio | a KPI is a share: outcome ÷ base | on-time repairs ÷ repairs received |
| count | a KPI is a number of things per period | claims submitted per month |
| backlog | work arrives, is done, the rest waits | open claims = last month + new − closed |
| inventory | stock is received and used | replacement devices in the warehouse |
| mix | a total is split across groups | sales by channel |
| events | single events with times (calls, tickets) | support calls waiting in a queue |
| items | each customer/policy changes state over time | policies renewing or cancelling |
| case | one row per case with attributes and an outcome | claim approved yes/no |

To fill the form yourself (when SFM's own drafting does not fit, or there is no LLM key):
1. Start the use case with `~/.sfm/venv/bin/python -m sfm.cli new "<description>" <files>`.
2. `~/.sfm/venv/bin/python -m sfm.cli form <id>` lists the fields, with choices taken from the data.
3. Write the answers as JSON and use them: `sfm.cli form <id> form.json` (or `sfm.cli new ... --form form.json`).

## Rules that keep the numbers right

- A share KPI is `100 × sum(outcome) / sum(base)` over the period and groups. Never average percentages.
- What one row of the data is (one per month? per claim? per depot per month?) is confirmed with the user, never guessed.
- Baseline and scenario use the same random numbers and the same start; only the levers the user changes differ.
- Every number comes from SFM or from the project's `simulate()`. Never write a number yourself.
- Say where each effect comes from: a mechanism (capacity, a rule), a document (with its page), learned from the data,
  or an assumption. An assumption is shown as one.

## Changing a Level 2 project

| What to change | Where | Then |
|---|---|---|
| The process: stocks, flows, levers, KPIs, queues | `model/procspec.json` | `python scripts/compile.py <project>` |
| A rule in code, a parameter computed from a table | `model/custom.py` (`adjust(spec)`) | `python scripts/check.py <project>` |
| New logic of any kind | `simulate()` in `model/model.py` | keep its result form (SFM's engine form); `check.py` |
| An effect the business confirmed | `tests/expectations.json`: `{"lever", "kpi", "direction": 1 or -1, "why"}` | `check.py` |

The page is SFM's own model page: change the model, not the page.
