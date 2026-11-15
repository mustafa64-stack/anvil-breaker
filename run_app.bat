@echo off
title DSA Core Path - 15-Minute Protocol App
echo ========================================================
echo  DSA CORE PATH & 15-MINUTE PROTOCOL WORKSPACE
echo  Connecting to Brave & LeetCode Git Push Extension
echo ========================================================
echo.

cd /d "%~dp0"

echo [1/2] Verifying Python and dependencies...
python -c "import fastapi, uvicorn" 2>NUL
if errorlevel 1 (
    echo FastAPI or Uvicorn missing. Installing dependencies...
    python -m pip install fastapi uvicorn requests
)

echo [2/2] Launching DSA Protocol Command Center on http://127.0.0.1:8765 ...
start http://127.0.0.1:8765

python -m uvicorn server:app --host 127.0.0.1 --port 8765
pause

