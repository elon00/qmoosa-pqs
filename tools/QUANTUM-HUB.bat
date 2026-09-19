@echo off
setlocal
cd /d "%~dp0\.."
if exist tools\quantum_hub.py (
  set "HUB=tools\quantum_hub.py"
) else (
  set "HUB=quantum_hub.py"
)
python "%HUB%" %*
