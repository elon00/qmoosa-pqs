@echo off
setlocal
cd /d "%~dp0"
if exist tools\one-click-qpu-certify.py (
  set "RUNNER=tools\one-click-qpu-certify.py"
) else (
  set "RUNNER=one-click-qpu-certify.py"
)
echo =========================================================
echo   BOUNTYHUNTER OS: CANONICAL QPU 10/10 CERTIFICATION
echo   Target: Physical Superconducting QPU (Dilution Fridge)
echo =========================================================
python "%RUNNER%" %*
if errorlevel 1 (
  echo.
  echo [!] CERTIFICATION BLOCKED: Authentic physical provider evidence is missing or unauthenticated.
  echo [!] Ensure your IBM Quantum or Origin Quantum account has active compute units and valid tokens.
  echo [!] Fail-closed standard: No simulation or mock data can certify a 10/10 QPU execution.
  exit /b 2
)
echo.
echo [*] STATUS: CERTIFIED_10_OF_10 (Physical QPU Execution Verified)