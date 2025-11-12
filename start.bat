@echo off
echo Starting Blockchain + AI Powered Plagiarism Detection System

REM Check if virtual environment exists
if not exist "venv" (
    echo ERROR: Virtual environment not found. Please run setup.py first.
    pause
    exit /b 1
)

REM Activate virtual environment and start application
call venv\Scripts\activate
python app.py
pause
