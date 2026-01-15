@echo off
setlocal enabledelayedexpansion
title FIB Manager - Application Launcher

:: Change to project root directory
cd /d "%~dp0\.."

:: Check if virtual environment exists
if not exist ".venv\Scripts\activate" (
    echo Error: Virtual environment not found.
    echo Please run setup.bat first to initialize the environment.
    pause
    exit /b 1
)

:: Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate
if errorlevel 1 (
    echo Error: Failed to activate virtual environment!
    pause
    exit /b 1
)

:: Run the CLI app
fib-manager app %*