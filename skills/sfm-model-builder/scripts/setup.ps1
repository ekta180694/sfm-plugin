# Step 0 on Windows: the SFM environment in ~\.sfm\venv (see setup.sh). Set SFM_SOURCE to SFM's git URL with @tag.
$ErrorActionPreference = "Stop"
if (-not $env:SFM_SOURCE) { Write-Output "MISSING SFM_SOURCE: set it to SFM's git address with @v1.0.0"; exit 2 }
if (-not (Get-Command py -ErrorAction SilentlyContinue)) { Write-Output "MISSING python 3.12: install it from python.org"; exit 2 }
$venv = Join-Path $HOME ".sfm\venv"
if (-not (Test-Path "$venv\Scripts\python.exe")) { Write-Output "CREATING $venv"; py -3.12 -m venv $venv }
Write-Output "INSTALLING SFM from $env:SFM_SOURCE"
if (Test-Path $env:SFM_SOURCE) { & "$venv\Scripts\pip" install -q $env:SFM_SOURCE pytest } else { & "$venv\Scripts\pip" install -q "sfm @ $env:SFM_SOURCE" pytest }
& "$venv\Scripts\python" -c "import importlib.metadata as m, sfm.modelpage; print('OK sfm', m.version('sfm'))"
