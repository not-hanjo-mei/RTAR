@echo off
title REALITY Auto Reply Tool
echo Starting RTAR...
echo.

REM Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.12+ and add it to your PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist "venv" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Set console encoding
chcp 65001 > nul
color

REM Run the application
python main.py

echo.
echo RTAR has exited.
pause