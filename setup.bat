@echo off
cls
echo Setting up Python environment...

REM Upgrade pip to latest version
python -m pip install --upgrade pip || (
    echo Error upgrading pip. Continuing anyway...
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv .venv || (
    echo Failed to create virtual environment!
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate || (
    echo Failed to activate virtual environment!
    exit /b 1
)

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt || (
    echo Failed to install requirements!
    exit /b 1
)

REM Install package in development mode
echo Installing package in development mode...
pip install -e . || (
    echo Failed to install package!
    exit /b 1
)

echo Setup completed successfully.

REM Show help for the CLI tool
echo Displaying help for schedule-searcher...
schedule-searcher --help