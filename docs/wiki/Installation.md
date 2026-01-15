# Installation Guide

This guide covers all methods for installing and setting up FIB Manager on your system.

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [Option 1: Pre-built Executables](#option-1-pre-built-executables-recommended)
- [Option 2: Python Installation](#option-2-python-installation)
- [Option 3: Development Setup](#option-3-development-setup)
- [Verifying Installation](#verifying-installation)

---

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| OS | Windows 10+, Linux, macOS |
| Internet | Required for API access |
| Terminal | Windows Terminal, PowerShell, or any Unix terminal |

### For Python Installation

| Component | Requirement |
|-----------|-------------|
| Python | 3.8 or higher |
| pip | Latest version recommended |

---

## Option 1: Pre-built Executables (Recommended)

The easiest way to get started with FIB Manager.

### Step 1: Download

Visit the [Releases Page](https://github.com/zvictorium/fib-manager/releases) and download:

- **`FIB Manager.exe`** - Interactive console application (recommended for most users)
- **`fib-manager.exe`** - Command-line interface (for scripting and automation)

### Step 2: Run

Simply double-click the downloaded executable or run from terminal:

```bash
# Interactive mode
"FIB Manager.exe"

# CLI mode
fib-manager.exe schedules -s IES XC --start 9 --end 18
```

> **Note**: On first run, Windows SmartScreen may show a warning. Click "More info" → "Run anyway" to proceed.

---

## Option 2: Python Installation

### Step 1: Install Python

Ensure Python 3.8+ is installed:

```bash
python --version
# Should output: Python 3.8.x or higher
```

If not installed, download from [python.org](https://www.python.org/downloads/)

### Step 2: Clone or Download the Repository

```bash
# Clone with Git
git clone https://github.com/zvictorium/fib-manager.git
cd fib-manager

# Or download and extract the ZIP from GitHub
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
- `requests` - HTTP client for API calls
- `rich` - Beautiful terminal formatting
- `questionary` - Interactive prompts
- `pyfiglet` - ASCII art text
- `tqdm` - Progress bars

### Step 4: Run the Application

```bash
# Interactive mode
python -m app app

# CLI mode
python -m app schedules -s IES XC --start 9 --end 18
```

---

## Option 3: Development Setup

For contributors and developers who want to modify the code.

### Using Automated Scripts

**Windows:**
```batch
cd scripts
setup.bat
```

**Linux/macOS:**
```bash
cd scripts
chmod +x setup.sh
./setup.sh
```

### Manual Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   
   # Activate on Windows
   venv\Scripts\activate
   
   # Activate on Linux/macOS
   source venv/bin/activate
   ```

2. **Install in development mode:**
   ```bash
   pip install -e .
   ```

3. **Install development dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Building Executables

To create standalone executables:

**Windows:**
```batch
cd scripts
compile.bat
```

**Linux/macOS:**
```bash
cd scripts
chmod +x compile.sh
./compile.sh
```

---

## Verifying Installation

### Test Interactive Mode

```bash
fib-manager app
# Or: python -m app app
```

You should see the FIB Manager splash screen with the main menu.

### Test CLI Mode

```bash
fib-manager subjects -q 2025Q1 -l en
# Or: python -m app subjects -q 2025Q1 -l en
```

You should see a JSON output listing available subjects.

### Test Schedule Generation

```bash
fib-manager schedules -s IES XC --start 9 --end 18 -q 2025Q1
# Or: python -m app schedules -s IES XC --start 9 --end 18 -q 2025Q1
```

You should see JSON output with schedule combinations.

---

## Troubleshooting Installation

### "Python not found"

Ensure Python is in your system PATH. On Windows, reinstall Python and check "Add Python to PATH".

### "Module not found" errors

```bash
pip install -r requirements.txt --force-reinstall
```

### Permission errors on Linux/macOS

```bash
chmod +x scripts/*.sh
pip install --user -r requirements.txt
```

### API Connection Issues

Ensure you have internet access and can reach `https://api.fib.upc.edu/v2`

---

**← [Home](Home.md)** | **[Commands Reference →](Commands.md)**
