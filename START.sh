#!/bin/bash
# RTAR Startup Script for Linux/macOS

echo "Starting RTAR - REALITY Auto Reply Tool..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.12+."
    exit 1
fi

# Check if ADB is installed
if ! command -v adb &> /dev/null; then
    echo "Error: ADB is not installed. Please install Android Debug Bridge:"
    echo "Ubuntu/Debian: sudo apt install android-tools-adb"
    echo "macOS: brew install android-platform-tools"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start RTAR
echo "Starting RTAR..."
python3 main.py

# Deactivate virtual environment on exit
deactivate