@echo off
REM One-click start for Windows: creates the virtual environment on first run,
REM installs Flask, opens the browser, and starts the app. Press Ctrl+C to stop.
cd /d "%~dp0"
set PY=python
where python >nul 2>nul || set PY=py
if not exist venv\Scripts\activate.bat %PY% -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
start "" cmd /c "timeout /t 4 >nul & start http://127.0.0.1:5000"
python app.py
pause
