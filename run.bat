@echo off
echo Lead Scraper Bot Launcher
echo ========================

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
python -c "import pymongo" 2>nul
if errorlevel 1 (
    echo Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install requirements
        pause
        exit /b 1
    )
)

REM Run the application
echo Starting Lead Scraper Bot...
python main.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Application exited with error
    pause
)
