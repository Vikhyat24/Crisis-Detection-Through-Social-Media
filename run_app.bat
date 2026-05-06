@echo off
echo ============================================
echo   Crisis Sentinel - Starting Server...
echo ============================================
echo.
echo Checking dependencies...
".venv\Scripts\python.exe" -m pip install -r "Crisis\requirements.txt" --quiet 2>nul
echo.
echo Starting web server...
echo Open http://localhost:5000 in your browser
echo.
start "" http://localhost:5000
".venv\Scripts\python.exe" "Crisis\app_web.py"
pause
