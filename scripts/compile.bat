@echo off
setlocal enabledelayedexpansion

echo ====================================
echo    FIB Manager Compilation Script
echo ====================================
echo.

:: Change to project root directory
cd /d "%~dp0\.."

:: Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

:: Check if PyInstaller is installed
echo Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo Error: Failed to install PyInstaller
        pause
        exit /b 1
    )
) else (
    echo PyInstaller is already installed
)

:: Clean previous builds
if exist "build" (
    echo Cleaning previous build directory...
    rmdir /s /q build
)

if exist "dist" (
    echo Cleaning previous dist directory...
    rmdir /s /q dist
)

:: Create dist directory
mkdir dist 2>nul

:: Create wrapper script for app version
echo Creating wrapper script for app version...
echo import sys > temp_app_wrapper.py
echo import os >> temp_app_wrapper.py
echo sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src')) >> temp_app_wrapper.py
echo sys.argv.append('app') >> temp_app_wrapper.py
echo from app.__main__ import main >> temp_app_wrapper.py
echo if __name__ == '__main__': >> temp_app_wrapper.py
echo     main() >> temp_app_wrapper.py

:: Get pyfiglet fonts location
echo Finding pyfiglet fonts location...
for /f "delims=" %%i in ('python -c "import pyfiglet; import os; print(os.path.dirname(pyfiglet.__file__))"') do set PYFIGLET_PATH=%%i
echo Pyfiglet path: %PYFIGLET_PATH%

:: Compile the CLI application
echo.
echo ====================================
echo    Compiling fig-manager...
echo ====================================
echo.

pyinstaller --onefile ^
    --name "fig-manager" ^
    --icon src\logo.ico ^
    --distpath dist ^
    --workpath build ^
    --specpath . ^
    --clean ^
    --noconfirm ^
    --console ^
    --add-data "src;src" ^
    --add-data "%PYFIGLET_PATH%\fonts;pyfiglet\fonts" ^
    --hidden-import "app" ^
    --hidden-import "app.commands" ^
    --hidden-import "app.commands.command_line" ^
    --hidden-import "app.commands.search" ^
    --hidden-import "app.commands.subjects" ^
    --hidden-import "app.commands.marks" ^
    --hidden-import "app.core" ^
    --hidden-import "app.core.utils" ^
    --hidden-import "app.core.parser" ^
    --hidden-import "app.core.schedule_generator" ^
    --hidden-import "app.core.validator" ^
    --hidden-import "app.core.constants" ^
    --hidden-import "app.ui" ^
    --hidden-import "app.ui.interactive" ^
    --hidden-import "app.ui.ui" ^
    --hidden-import "app.api" ^
    --hidden-import "app.api.api" ^
    --hidden-import "requests" ^
    --hidden-import "rich" ^
    --hidden-import "questionary" ^
    --hidden-import "pyfiglet" ^
    --hidden-import "pyfiglet.fonts" ^
    --collect-data pyfiglet ^
    --hidden-import "argparse" ^
    --hidden-import "json" ^
    --paths src ^
    src/app/__main__.py

if errorlevel 1 (
    echo.
    echo ====================================
    echo     CLI Compilation FAILED!
    echo ====================================
    pause
    exit /b 1
)

:: Compile the APP application
echo.
echo ====================================
echo    Compiling FIB Manager APP...
echo ====================================
echo.

pyinstaller --onefile ^
    --name "FIB Manager" ^
    --icon src\logo.ico ^
    --distpath dist ^
    --workpath build ^
    --specpath . ^
    --clean ^
    --noconfirm ^
    --console ^
    --add-data "src;src" ^
    --add-data "%PYFIGLET_PATH%\fonts;pyfiglet\fonts" ^
    --hidden-import "app" ^
    --hidden-import "app.commands" ^
    --hidden-import "app.commands.command_line" ^
    --hidden-import "app.commands.search" ^
    --hidden-import "app.commands.subjects" ^
    --hidden-import "app.commands.marks" ^
    --hidden-import "app.core" ^
    --hidden-import "app.core.utils" ^
    --hidden-import "app.core.parser" ^
    --hidden-import "app.core.schedule_generator" ^
    --hidden-import "app.core.validator" ^
    --hidden-import "app.core.constants" ^
    --hidden-import "app.ui" ^
    --hidden-import "app.ui.interactive" ^
    --hidden-import "app.ui.ui" ^
    --hidden-import "app.api" ^
    --hidden-import "app.api.api" ^
    --hidden-import "requests" ^
    --hidden-import "rich" ^
    --hidden-import "questionary" ^
    --hidden-import "pyfiglet" ^
    --hidden-import "pyfiglet.fonts" ^
    --collect-data pyfiglet ^
    --hidden-import "argparse" ^
    --hidden-import "json" ^
    --paths src ^
    temp_app_wrapper.py

if errorlevel 1 (
    echo.
    echo ====================================
    echo     APP Compilation FAILED!
    echo ====================================
    del temp_app_wrapper.py 2>nul
    pause
    exit /b 1
)

:: Clean up wrapper script
del temp_app_wrapper.py 2>nul

:: Check if executables were created
set CLI_EXISTS=0
set APP_EXISTS=0

if exist "dist\fig-manager.exe" (
    set CLI_EXISTS=1
)

if exist "dist\FIB Manager.exe" (
    set APP_EXISTS=1
)

if %CLI_EXISTS%==1 if %APP_EXISTS%==1 (
    echo.
    echo ====================================
    echo     Compilation SUCCESSFUL!
    echo ====================================
    echo.
    echo CLI Executable created: dist\fig-manager.exe
    dir "dist\fig-manager.exe" | find "fig-manager.exe"
    echo.
    echo APP Executable created: dist\FIB Manager.exe
    dir "dist\FIB Manager.exe" | find "FIB Manager.exe"
    echo.
    echo Usage:
    echo   CLI: "dist\fig-manager.exe" [commands]
    echo   APP: "dist\FIB Manager.exe"
    echo.
) else (
    echo.
    echo ====================================
    echo     Compilation FAILED!
    echo ====================================
    if %CLI_EXISTS%==0 echo CLI executable not found in dist directory
    if %APP_EXISTS%==0 echo APP executable not found in dist directory
    pause
    exit /b 1
)

:: Clean up build artifacts (optional)
echo Cleaning build artifacts...
if exist "build" rmdir /s /q build
if exist "fig-manager.spec" del "fig-manager.spec"
if exist "FIB Manager.spec" del "FIB Manager.spec"

echo.
echo ====================================
echo       Compilation Complete!
echo ====================================
echo.

pause
