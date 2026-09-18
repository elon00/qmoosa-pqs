@echo off
setlocal
cd /d "%~dp0.."
echo QMoosa-PQS ONE-CLICK QPU CERTIFICATION
echo =====================================
python tools\one-click-qpu-certify.py
if errorlevel 1 (
  echo.
  echo CERTIFICATION BLOCKED: real provider evidence is missing or invalid.
  echo Configure the provider account/secret, run the provider execution step,
  echo then rerun this launcher. Do NOT paste secrets into chat.
  exit /b 2
)
echo.
echo CERTIFIED_10_OF_10
