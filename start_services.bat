@echo off
echo 🏥 Starting Drug Risk Prediction System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Install requirements if needed
echo 📦 Checking requirements...
pip install -r requirements.txt

echo.
echo 🚀 Starting services...
echo.

REM Start the startup script
python start_services.py

pause
