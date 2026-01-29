# RTAR Launcher Script

$ErrorActionPreference = "Stop"

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.12+ and add it to your PATH"
    Read-Host -Prompt "Press Enter to exit"
    exit 1
}

$venvPath = ".venv"
$venvPython = "$venvPath\Scripts\python.exe"

# Check if virtual environment exists
if (-not (Test-Path $venvPath)) {
    Write-Host "Virtual environment not found."
    $createVenv = Read-Host -Prompt "Do you want to create one? (y/n)"

    if ($createVenv -eq "y" -or $createVenv -eq "Y") {
        Write-Host "Creating virtual environment..."
        python -m venv $venvPath
        Write-Host "Installing dependencies..."
        & $venvPython -m pip install -e .
    } else {
        Write-Host "Virtual environment creation skipped. Please create one manually if needed."
        Read-Host -Prompt "Press Enter to exit"
        exit 1
    }
}

Write-Host "Starting RTAR..." -ForegroundColor Green
Write-Host "Tip: Copy .env.example to .env to customize host/port" -ForegroundColor Gray

# Run the application directly from venv
try {
    & $venvPython main.py
} finally {
    Write-Host ""
    Write-Host "RTAR has exited." -ForegroundColor Green
}
