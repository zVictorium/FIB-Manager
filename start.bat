@echo off
cls
echo Starting fib-horarios app...

REM ensure virtual environment exists
if not exist ".venv\Scripts\activate" (
    echo Virtual environment not found. Run setup.bat first.
    exit /b 1
)

REM activate virtual environment
call .venv\Scripts\activate || (
    echo Failed to activate virtual environment!
    exit /b 1
)

REM run the CLI app
fib-horarios app %*

pause
