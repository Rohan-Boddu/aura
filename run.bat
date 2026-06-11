@echo off
cd /d "%~dp0"

echo.
echo ============================================
echo   AURA 4.0 Server
echo ============================================
echo.
echo Starting server on http://localhost:5000
echo.
echo If you get import errors, run this first:
echo   pip install flask requests
echo.

start http://localhost:5000

python server.py

pause
