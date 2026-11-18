# Checkpoints (Level 2)

At the end of every step:

1. Write the step record to a file and save it: `python scripts/step.py <project> <n> <file>`.
2. Make sure the page runs (`<project>/run.sh`); the record shows in the Building Model tab.
3. Tell the user: "Step n of 8: <name>. <2-4 lines>. Diagrams and details: http://127.0.0.1:8900/apps/project?tab=building".
4. Ask: **Approve**, **Give feedback**, or **Go back** (to which step).
5. Record the answer: `python scripts/decide.py <project> <n> approve|feedback|back --text "<their words>" --who "<name>"`.
   If they approved in the tab instead and just say "continue", read the newest decision for step n in
   `build/decisions.json`.

A step record (JSON). Diagrams are Mermaid text; the tab draws them.

```json
{"title": "Business", "summary": "Repair depots: the on-time repair rate is the main KPI; parts pre-stock is the lever.",
 "findings": ["KPI on-time rate = 100 × sum(repairs_on_time) / sum(repairs_received) (brief p.2)",
              "Lever parts_prestock_pct, 20-50% in history"],
 "tables": [{"title": "KPIs", "columns": ["KPI", "Formula", "Source"],
             "rows": [["On-time rate", "100 × sum(on_time) / sum(received)", "brief p.2"]]}],
 "diagrams": ["flowchart LR\n  prestock[Parts pre-stock] --> ontime[On-time rate]\n  volume[Repairs received] --> ontime"],
 "messages": [{"who": "assistant", "text": "I read the brief and the data; here are the KPIs and the lever."}]}
```
