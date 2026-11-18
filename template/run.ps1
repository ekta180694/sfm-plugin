Set-Location $PSScriptRoot
$py = if ($env:PYTHON) { $env:PYTHON } else { Join-Path $HOME ".sfm\venv\Scripts\python.exe" }
& $py ui\server.py
