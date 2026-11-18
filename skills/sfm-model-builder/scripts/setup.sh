#!/bin/bash
# Step 0: the SFM environment in ~/.sfm/venv (SFM at a pinned version). SFM_SOURCE: a git URL with @tag, or a folder.
# One line per stage so the assistant can show progress.
set -e
SRC="${SFM_SOURCE:-/data/projects/ekta/Simulation AI}"
PY=$(command -v python3.12 || true)
[ -z "$PY" ] && { echo "MISSING python3.12: install Python 3.12, then run this again"; exit 2; }
echo "OK python: $PY"
[ -x "$HOME/.sfm/venv/bin/python" ] || { echo "CREATING ~/.sfm/venv"; "$PY" -m venv "$HOME/.sfm/venv"; }
echo "INSTALLING SFM from $SRC (a few minutes the first time)"
if [ -d "$SRC" ]; then "$HOME/.sfm/venv/bin/pip" install -q "$SRC" pytest; else "$HOME/.sfm/venv/bin/pip" install -q "sfm @ $SRC" pytest; fi
"$HOME/.sfm/venv/bin/python" -c "import importlib.metadata as m, sfm.modelpage, sfm.mcp_server; print('OK sfm', m.version('sfm'))"
