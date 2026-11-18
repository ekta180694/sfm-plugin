---
name: sfm-model-builder
description: Build a simulation model of a business with a UI to use it, step by step, with the user approving every step. Level 1 uses SFM as it is (through the sfm MCP tools); Level 2 makes the model the user's own project, which they can change without limits, with the same model page. Use when the user wants to build, continue or change a simulation model, a what-if model, or "a model like Control Tower".
---

# Build a simulation model, step by step

Guide the user from nothing to a working model with a UI. Plain, simple English. One thing at a time. Always say
where they are: "Step 4 of 8: the data". Never invent a number: every figure comes from SFM or from the project's
`simulate()`. Never ask for, type or store a password. Scripts are in this skill's `scripts/` folder.

## Step 0: setup (first time; later a quick re-check)

One item at a time; show ✓ or what is needed; fix it or ask; then go on.

1. Python 3.12: `python3.12 --version` (Windows: `py -3.12 --version`). If missing, say how to install it and wait.
2. SFM environment: if `~/.sfm/venv/bin/python` is missing, offer to run `scripts/setup.sh` (Windows: `scripts/setup.ps1`);
   show its lines as progress; on failure show the error and the one fix it names.
3. Which SFM: call the MCP tool `sfm_connect` and explain the result in one line:
   - deployed: models are shared and hosted on the SFM service;
   - local: SFM runs on this machine only. If `llm` is false: the Azure OpenAI key goes in `~/.saim/aoai.key` or
     `AZURE_OPENAI_KEY`, or work without it (SFM then builds from a model form you fill together);
   - none: help fix the address or the setup; nothing else can start without SFM.
   If `signed_in` is false: the user runs `sfm login <their name>` themselves in a terminal
   (`~/.sfm/venv/bin/python -m sfm.cli login <name>`), then call `sfm_connect` again. You never handle the password.
4. Summary line: "Ready: <mode> SFM, signed in as <name>, Python ✓".

## Start

Ask: what to simulate and why; where the documents and data are; the level:
- **Level 1**: SFM builds it; later changes are limited to what SFM allows; it becomes an app on SFM.
- **Level 2**: your own project, changeable without limits (process, logic, rules, engine), hosted on its own, with the
  same model page.

## Level 1

1. `sfm_create_use_case` with the description and files (local files are uploaded).
2. After each SFM step: `sfm_status`; give a 2-4 line summary and its `link` ("diagrams and details here").
3. Ask **Approve**, **Give feedback** or **Go back**. Approve → `sfm_approve` (the build needs a technical and a business
   sign-off: role and name). Feedback → `sfm_message`. They may approve on the card instead; check with `sfm_status`.
4. If SFM cannot build it: show SFM's reason; offer to fill the model form together (`method/modelling.md`), or Level 2.
5. End: the app link (`sfm_apps`); its first tab, Building Model, shows how it was built.

## Level 2

Create the project: ask for a new folder, confirm, `python scripts/new_project.py <folder>`.

**At every checkpoint** (details in `method/checkpoints.md`): save the step record with `scripts/step.py`, make sure the
page runs, say "Step n of 8: <name>" with a short summary and the link
http://127.0.0.1:8900/apps/project?tab=building, ask **Approve**, **Give feedback** or **Go back**, and record the answer
with `scripts/decide.py`. Approve → next step. Feedback → redo this step with it. Go back → that step; later steps are
redone.

**Step 1 of 8: set up.** Start the page (`<project>/run.sh` in the background), check it opens, ask the user to confirm.
**Step 2 of 8: inputs.** Read the documents, data and links. Copy the data files into `<project>/data/` (keep their names).
**Step 3 of 8: business.** Objective, questions, KPIs with formulas (with the source), drivers, levers; a driver → KPI diagram.
**Step 4 of 8: data.** What one row is (with evidence), the time column, each column's role. Never guess the grain: ask.
**Step 5 of 8: core model with SFM.** `sfm_create_use_case` with the description and the files, and take SFM through its
steps with the user's agreement at each (as in Level 1). If SFM's own drafting does not fit, fill the model form together
(`method/modelling.md`). Then `sfm_export` to a file and `python scripts/export.py <project> <file> --data <the files in
data/>`. If it lists missing tables, ask for them.
**Step 6 of 8: process and logic.** Deeper changes in the project (`method/modelling.md`): the process in
`model/procspec.json` (then `python scripts/compile.py <project>`), code rules in `model/custom.py`, or new logic in
`simulate()` in `model/model.py` (keep its result form). Show the process diagram. Add each approved effect direction to
`tests/expectations.json`.
**Step 7 of 8: build and check.** `python scripts/check.py <project>`; show the results. If a check fails, fix it before
asking for approval.
**Step 8 of 8: UI.** Walk through the tabs with the user (Building Model, Baseline, Scenario Studio, Optimize & ROI).
The page is SFM's own model page; change the model, not the page.

**End:** summary; `./run.sh`; hosting with the `Dockerfile` (`SHOW_BUILD_TAB=0` hides the build history); later changes:
just ask.

## Changes after the build (any depth)

Edit, run `python scripts/check.py <project>`, write `build/changes/<n>.json` (`{what, files, kpis_before, kpis_after,
tests}`, with numbers from the page's Scenario Studio before and after), show it, ask for approval. Never offer a change
whose checks fail.

## Resuming

`/sfm:continue`: read `build/journey.json`, say the step, read the latest decision, continue.
