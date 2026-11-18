#!/bin/bash
# The model page: http://127.0.0.1:8900 (SFM_UI_PORT to change). Uses ~/.sfm/venv unless PYTHON is set.
cd "$(dirname "$0")"
exec "${PYTHON:-$HOME/.sfm/venv/bin/python}" ui/server.py
