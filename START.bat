@echo off
title REALITY Auto Reply Tool

REM Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.12+ and add it to your PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv" (
    echo Virtual environment not found.
    echo Do you want to create one? (y/n)
    set /p create_venv=
    if /i "%create_venv%"=="y" (
        echo Creating virtual environment...
        python -m venv .venv
        call .venv\Scripts\activate.bat
        echo Installing dependencies...
        python -m pip install -e .
    ) else (
        echo Virtual environment creation skipped. Please create one manually if needed.
        pause
        exit /b 1
    )
)
echo Starting RTAR...
REM Set console encoding
chcp 65001 > nul
color

echo Starting RTAR...
echo Tip: Copy .env.example to .env to customize host/port
REM Run the application
.\.venv\Scripts\python.exe main.py

echo.
echo RTAR has exited.
pause