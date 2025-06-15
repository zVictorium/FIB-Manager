#!/bin/bash

echo "===================================="
echo "    FIB Manager Compilation Script"
echo "===================================="
echo

# Change to project root directory
cd "$(dirname "$0")/.."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
    echo "Virtual environment created successfully."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment"
    exit 1
fi
echo "Virtual environment activated successfully."

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi
echo "Dependencies installed successfully."

# Check if PyInstaller is installed
echo "Checking PyInstaller..."
pip show pyinstaller > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install PyInstaller"
        exit 1
    fi
    echo "PyInstaller installed successfully."
else
    echo "PyInstaller is already installed."
fi

# Clean previous builds
if [ -d "build" ]; then
    echo "Cleaning previous build directory..."
    rm -rf build
fi

if [ -d "dist" ]; then
    echo "Cleaning previous dist directory..."
    rm -rf dist
fi

# Create dist directory
mkdir -p dist

# Create wrapper script for app version
echo "Creating wrapper script for app version..."
cat > temp_app_wrapper.py << 'EOF'
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.argv.append('app')
from app.__main__ import main
if __name__ == '__main__':
    main()
EOF

# Get pyfiglet fonts location
echo "Finding pyfiglet fonts location..."
PYFIGLET_PATH=$(python3 -c "import pyfiglet; import os; print(os.path.dirname(pyfiglet.__file__))")
echo "Pyfiglet path: $PYFIGLET_PATH"

# Compile the CLI application
echo
echo "===================================="
echo "    Compiling CLI Application..."
echo "===================================="
echo

pyinstaller --onefile \
    --name "fig-manager" \
    --icon docs/logo/logo.ico \
    --distpath dist \
    --workpath build \
    --specpath . \
    --clean \
    --noconfirm \
    --console \
    --add-data "src:src" \
    --add-data "$PYFIGLET_PATH/fonts:pyfiglet/fonts" \
    --hidden-import "app" \
    --hidden-import "app.commands" \
    --hidden-import "app.commands.command_line" \
    --hidden-import "app.commands.search" \
    --hidden-import "app.commands.subjects" \
    --hidden-import "app.commands.marks" \
    --hidden-import "app.core" \
    --hidden-import "app.core.utils" \
    --hidden-import "app.core.parser" \
    --hidden-import "app.core.schedule_generator" \
    --hidden-import "app.core.validator" \
    --hidden-import "app.core.constants" \
    --hidden-import "app.ui" \
    --hidden-import "app.ui.interactive" \
    --hidden-import "app.ui.ui" \
    --hidden-import "app.api" \
    --hidden-import "app.api.api" \
    --hidden-import "requests" \
    --hidden-import "rich" \
    --hidden-import "questionary" \
    --hidden-import "pyfiglet" \
    --hidden-import "pyfiglet.fonts" \
    --collect-data pyfiglet \
    --hidden-import "argparse" \
    --hidden-import "json" \
    --paths src \
    src/app/__main__.py

if [ $? -ne 0 ]; then
    echo
    echo "===================================="
    echo "     CLI Compilation FAILED!"
    echo "===================================="
    exit 1
fi

echo "CLI application compiled successfully."

# Compile the APP application
echo
echo "===================================="
echo "    Compiling APP Application..."
echo "===================================="
echo

pyinstaller --onefile \
    --name "FIB Manager" \
    --icon docs/logo/logo.ico \
    --distpath dist \
    --workpath build \
    --specpath . \
    --clean \
    --noconfirm \
    --console \
    --add-data "src:src" \
    --add-data "$PYFIGLET_PATH/fonts:pyfiglet/fonts" \
    --hidden-import "app" \
    --hidden-import "app.commands" \
    --hidden-import "app.commands.command_line" \
    --hidden-import "app.commands.search" \
    --hidden-import "app.commands.subjects" \
    --hidden-import "app.commands.marks" \
    --hidden-import "app.core" \
    --hidden-import "app.core.utils" \
    --hidden-import "app.core.parser" \
    --hidden-import "app.core.schedule_generator" \
    --hidden-import "app.core.validator" \
    --hidden-import "app.core.constants" \
    --hidden-import "app.ui" \
    --hidden-import "app.ui.interactive" \
    --hidden-import "app.ui.ui" \
    --hidden-import "app.api" \
    --hidden-import "app.api.api" \
    --hidden-import "requests" \
    --hidden-import "rich" \
    --hidden-import "questionary" \
    --hidden-import "pyfiglet" \
    --hidden-import "pyfiglet.fonts" \
    --collect-data pyfiglet \
    --hidden-import "argparse" \
    --hidden-import "json" \
    --paths src \
    temp_app_wrapper.py

if [ $? -ne 0 ]; then
    echo
    echo "===================================="
    echo "     APP Compilation FAILED!"
    echo "===================================="
    rm -f temp_app_wrapper.py
    exit 1
fi

echo "APP application compiled successfully."

# Clean up wrapper script
rm -f temp_app_wrapper.py

# Check if executables were created
CLI_EXISTS=0
APP_EXISTS=0

if [ -f "dist/fig-manager" ]; then
    CLI_EXISTS=1
fi

if [ -f "dist/FIB Manager" ]; then
    APP_EXISTS=1
fi

if [ $CLI_EXISTS -eq 1 ] && [ $APP_EXISTS -eq 1 ]; then
    echo
    echo "===================================="
    echo "     Compilation SUCCESSFUL!"
    echo "===================================="
    echo
    echo "CLI Executable: dist/fig-manager"
    ls -la "dist/fig-manager"
    echo
    echo "APP Executable: dist/FIB Manager"
    ls -la "dist/FIB Manager"
    echo
    echo "Usage:"
    echo "  CLI: \"dist/fig-manager\" [commands]"
    echo "  APP: \"dist/FIB Manager\""
    echo
else
    echo
    echo "===================================="
    echo "     Compilation FAILED!"
    echo "===================================="
    if [ $CLI_EXISTS -eq 0 ]; then
        echo "Error: CLI executable not found in dist directory"
    fi
    if [ $APP_EXISTS -eq 0 ]; then
        echo "Error: APP executable not found in dist directory"
    fi
    exit 1
fi

# Clean up build artifacts
echo "Cleaning build artifacts..."
rm -rf build
rm -f "fig-manager.spec"
rm -f "FIB Manager.spec"

echo
echo "===================================="
echo "     Compilation Complete!"
echo "===================================="
echo

read -p "Press Enter to continue..."
