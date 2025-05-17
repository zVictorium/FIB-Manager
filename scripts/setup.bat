@echo off
title FIB Manager Installer
cls
echo Setting up Python environment...

REM Upgrade pip to latest version
python -m pip install --upgrade pip || (
    echo Failed to upgrade pip!
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv ..\.venv || (
    echo Failed to create virtual environment!
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call ..\.venv\Scripts\activate || (
    echo Failed to activate virtual environment!
    pause
    exit /b 1
)

REM Install requirements
echo Installing dependencies...
pip install -r ..\requirements.txt || (
    echo Failed to install dependencies!
    pause
    exit /b 1
)

REM Install package in development mode
echo Installing package in development mode...
cd .. && pip install -e . || (
    echo Failed to install package in development mode!
    pause
    exit /b 1
)
cd scripts

echo Setup completed successfully.

REM Show help for the CLI tool
echo Displaying help for fib-manager...
fib-manager --help

pause