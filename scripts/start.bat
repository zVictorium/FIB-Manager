@echo off
title FIB Manager
cls
REM ensure virtual environment exists
if not exist "..\\.venv\Scripts\activate" (
    echo Virtual environment not found. Run setup.bat first.
    pause
    exit /b 1
)

REM activate virtual environment
call ..\\.venv\Scripts\activate || (
    echo Failed to activate virtual environment!
    pause
    exit /b 1
)

REM run the CLI app
fib-manager app %*