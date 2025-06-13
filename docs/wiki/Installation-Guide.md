# Installation Guide

Complete installation instructions for FIB Manager across all supported platforms and use cases.

## System Requirements

### Minimum Requirements
- **Operating System:** Windows 10, macOS 10.14, or Linux (Ubuntu 18.04+)
- **RAM:** 512 MB available memory
- **Storage:** 100 MB free disk space
- **Network:** Internet connection for API access

### Recommended Requirements
- **Operating System:** Windows 11, macOS 12+, or Linux (Ubuntu 20.04+)
- **RAM:** 1 GB available memory
- **Storage:** 500 MB free disk space
- **Terminal:** Modern terminal with ANSI color support

### For Python Development
- **Python:** Version 3.8 or higher
- **pip:** Latest version (≥21.0)
- **Virtual Environment:** venv or virtualenv support

## Installation Methods

### Method 1: Pre-built Executables (Recommended for End Users)

This is the easiest method for users who just want to use FIB Manager without setting up a Python environment.

#### Windows

1. **Download Executables**
   - Visit the [Releases Page](https://github.com/zvictorium/fib-manager/releases)
   - Download the latest Windows release files:
     - `FIB Manager.exe` - Interactive console application
     - `fib-manager.exe` - Command-line interface

2. **Choose Installation Location**
   ```cmd
   # Create a dedicated folder (recommended)
   mkdir "C:\Program Files\FIB Manager"
   cd "C:\Program Files\FIB Manager"
   
   # Or use your preferred location
   mkdir "C:\Users\%USERNAME%\FIB-Manager"
   cd "C:\Users\%USERNAME%\FIB-Manager"
   ```

3. **Move Executables**
   - Copy the downloaded `.exe` files to your chosen folder
   - Optionally, add the folder to your system PATH

4. **Verify Installation**
   ```cmd
   # Test CLI version
   "C:\Program Files\FIB Manager\fib-manager.exe" --help
   
   # Test interactive version
   "C:\Program Files\FIB Manager\FIB Manager.exe"
   ```

#### macOS

1. **Download Executables**
   - Visit the [Releases Page](https://github.com/zvictorium/fib-manager/releases)
   - Download the latest macOS release files
   - Extract if provided as `.zip` or `.tar.gz`

2. **Install to Applications**
   ```bash
   # Create application folder
   sudo mkdir -p /Applications/FIB-Manager
   
   # Move executables
   sudo mv fib-manager /Applications/FIB-Manager/
   sudo mv "FIB Manager" /Applications/FIB-Manager/
   
   # Make executable
   sudo chmod +x /Applications/FIB-Manager/*
   ```

3. **Add to PATH (Optional)**
   ```bash
   # Add to ~/.zshrc or ~/.bash_profile
   echo 'export PATH="/Applications/FIB-Manager:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

4. **Verify Installation**
   ```bash
   # Test CLI version
   /Applications/FIB-Manager/fib-manager --help
   
   # If added to PATH
   fib-manager --help
   ```

#### Linux

1. **Download Executables**
   - Visit the [Releases Page](https://github.com/zvictorium/fib-manager/releases)
   - Download the latest Linux release files

2. **Install System-wide**
   ```bash
   # Create installation directory
   sudo mkdir -p /opt/fib-manager
   
   # Move executables
   sudo mv fib-manager /opt/fib-manager/
   sudo mv "FIB Manager" /opt/fib-manager/
   
   # Make executable
   sudo chmod +x /opt/fib-manager/*
   
   # Create symlinks (optional)
   sudo ln -s /opt/fib-manager/fib-manager /usr/local/bin/fib-manager
   ```

3. **User Installation Alternative**
   ```bash
   # Install to user directory
   mkdir -p ~/.local/bin
   mv fib-manager ~/.local/bin/
   chmod +x ~/.local/bin/fib-manager
   
   # Ensure ~/.local/bin is in PATH
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

4. **Verify Installation**
   ```bash
   fib-manager --help
   ```

### Method 2: Quick Setup Script (Recommended for Developers)

This method sets up a complete Python development environment with FIB Manager.

#### Windows

1. **Prerequisites**
   - Install [Python 3.8+](https://python.org/downloads/) with pip
   - Install [Git](https://git-scm.com/downloads) (optional, for cloning)

2. **Download Project**
   ```cmd
   # Option A: Clone with Git
   git clone https://github.com/zvictorium/fib-manager.git
   cd fib-manager
   
   # Option B: Download ZIP
   # Download and extract ZIP from GitHub, then:
   cd fib-manager
   ```

3. **Run Setup Script**
   ```cmd
   # Execute automated setup
   .\scripts\setup.bat
   ```

   The script will:
   - Create a virtual environment
   - Install all dependencies
   - Install FIB Manager in development mode
   - Run verification tests

4. **Manual Activation**
   ```cmd
   # For future sessions, activate the environment
   .venv\Scripts\activate
   fib-manager --help
   ```

#### macOS/Linux

1. **Prerequisites**
   ```bash
   # macOS (using Homebrew)
   brew install python3 git
   
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip python3-venv git
   
   # CentOS/RHEL/Fedora
   sudo dnf install python3 python3-pip git
   ```

2. **Download Project**
   ```bash
   # Clone repository
   git clone https://github.com/zvictorium/fib-manager.git
   cd fib-manager
   ```

3. **Run Setup**
   ```bash
   # Make setup script executable
   chmod +x scripts/setup.sh
   
   # Run automated setup
   ./scripts/setup.sh
   ```

4. **Manual Activation**
   ```bash
   # For future sessions
   source .venv/bin/activate
   fib-manager --help
   ```

### Method 3: Manual Python Installation

For advanced users who want complete control over the installation process.

#### Step 1: Environment Setup

**Windows:**
```cmd
# Create virtual environment
python -m venv fib-manager-env

# Activate environment
fib-manager-env\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip
```

**macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv fib-manager-env

# Activate environment
source fib-manager-env/bin/activate

# Upgrade pip
pip install --upgrade pip
```

#### Step 2: Install Dependencies

```bash
# Download project
git clone https://github.com/zvictorium/fib-manager.git
cd fib-manager

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

#### Step 3: Verify Installation

```bash
# Test CLI
fib-manager --help

# Test basic functionality
fib-manager subjects --help

# Test interactive mode (if supported)
fib-manager app
```

### Method 4: PyPI Installation (Future Release)

Once FIB Manager is published to PyPI, you can install it directly:

```bash
# Install from PyPI (future release)
pip install fib-manager

# Verify installation
fib-manager --help
```

## Post-Installation Configuration

### Terminal Setup

**Windows Users:**
- **Recommended:** Use Windows Terminal or PowerShell
- **Avoid:** Command Prompt (cmd.exe) for interactive mode
- **Enable:** ANSI color support in terminal settings

**macOS Users:**
- **Built-in Terminal:** Works well with default settings
- **iTerm2:** Excellent compatibility (recommended)
- **VS Code Terminal:** Full compatibility

**Linux Users:**
- **Most terminals:** Excellent compatibility
- **Required:** ANSI color support (standard in modern terminals)

### Environment Variables (Optional)

Set these environment variables for customization:

```bash
# Windows
set FIB_DEFAULT_LANGUAGE=en
set FIB_DEBUG=false

# macOS/Linux
export FIB_DEFAULT_LANGUAGE=en
export FIB_DEBUG=false
```

Available variables:
- `FIB_DEFAULT_LANGUAGE`: Default language (`en`, `es`, `ca`)
- `FIB_DEBUG`: Enable debug logging (`true`/`false`)
- `FIB_CACHE_TIMEOUT`: API cache timeout in seconds

### Path Configuration

**Add to System PATH (Optional):**

**Windows:**
1. Open System Properties → Advanced → Environment Variables
2. Edit PATH variable
3. Add FIB Manager installation directory

**macOS/Linux:**
```bash
# Add to ~/.bashrc, ~/.zshrc, or ~/.profile
export PATH="$PATH:/path/to/fib-manager"
```

## Verification and Testing

### Basic Functionality Test

```bash
# Test CLI help
fib-manager --help

# Test API connectivity
fib-manager subjects

# Test schedule generation (basic)
fib-manager schedules -s IES XC

# Test interactive mode (if available)
fib-manager app
```

### Advanced Testing

```bash
# Test with specific quadrimester
fib-manager subjects -q 2024Q1 -l en

# Test schedule generation with options
fib-manager schedules -s IES XC --start 9 --end 18 -l en es

# Test grade calculator (Beta)
fib-manager marks --formula "EX1*0.6+EX2*0.4" --target 7.0 --values EX1=6.0
```

### Performance Test

```bash
# Time a schedule generation request
time fib-manager schedules -s IES XC PROP

# Test with multiple subjects (performance check)
fib-manager schedules -s IES XC PROP BD SO
```

## Troubleshooting Installation

### Common Issues

**"Python not found" or "command not found"**
- **Cause:** Python not installed or not in PATH
- **Solution:** Install Python 3.8+ and ensure it's in system PATH
- **Verify:** `python --version` or `python3 --version`

**"pip not found"**
- **Cause:** pip not installed with Python
- **Solution:** Install pip manually or reinstall Python with pip
- **Verify:** `pip --version`

**"Permission denied" (Linux/macOS)**
- **Cause:** Insufficient permissions for installation directory
- **Solution:** Use `sudo` for system installation or install to user directory
- **Alternative:** Use virtual environment (recommended)

**"Virtual environment creation failed"**
- **Cause:** venv module not available
- **Solution:** Install python3-venv package
- **Linux:** `sudo apt install python3-venv`

**"ModuleNotFoundError" when running**
- **Cause:** Dependencies not installed or wrong environment
- **Solution:** Activate virtual environment and reinstall dependencies
- **Verify:** `pip list` shows required packages

**"Interactive mode not working"**
- **Cause:** Terminal doesn't support ANSI colors or Windows compatibility
- **Solution:** Use modern terminal (Windows Terminal, PowerShell, iTerm2)
- **Workaround:** Use CLI mode instead of interactive mode

### Dependency Issues

**Conflicting package versions:**
```bash
# Create fresh environment
python -m venv fresh-env
source fresh-env/bin/activate  # or fresh-env\Scripts\activate on Windows
pip install -r requirements.txt
pip install -e .
```

**Missing system libraries (Linux):**
```bash
# Ubuntu/Debian
sudo apt install python3-dev build-essential

# CentOS/RHEL/Fedora
sudo dnf install python3-devel gcc
```

### Network Issues

**API connection problems:**
```bash
# Test basic connectivity
ping raco.fib.upc.edu

# Test with curl
curl -I https://raco.fib.upc.edu/api/

# Use debug mode
export FIB_DEBUG=true
fib-manager subjects
```

**Proxy or firewall issues:**
```bash
# Configure pip for proxy
pip install --proxy http://proxy.server:port package

# Set environment variables
export HTTP_PROXY=http://proxy.server:port
export HTTPS_PROXY=http://proxy.server:port
```

## Uninstallation

### Remove Executables

**Windows:**
```cmd
# Remove installation directory
rmdir /s "C:\Program Files\FIB Manager"

# Remove from PATH if added
# Edit system environment variables manually
```

**macOS/Linux:**
```bash
# Remove installation
sudo rm -rf /opt/fib-manager
sudo rm -f /usr/local/bin/fib-manager

# Or for user installation
rm -rf ~/.local/bin/fib-manager
```

### Remove Python Installation

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment directory
rm -rf fib-manager-env  # or .venv

# Remove project directory
rm -rf fib-manager
```

### Clean System Configuration

```bash
# Remove environment variables (edit shell configuration files)
# ~/.bashrc, ~/.zshrc, ~/.profile on macOS/Linux
# System Environment Variables on Windows

# Clear any cached data (if applicable)
rm -rf ~/.cache/fib-manager  # Future feature
```

## Upgrade Instructions

### Executable Upgrades

1. Download latest release from GitHub
2. Replace old executables with new ones
3. Test functionality

### Python Installation Upgrades

```bash
# Activate environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Update repository
git pull origin main  # if using git

# Update dependencies
pip install -r requirements.txt --upgrade

# Reinstall package
pip install -e . --force-reinstall

# Verify upgrade
fib-manager --version
```

## Getting Help

If you encounter issues during installation:

1. **Check Requirements:** Ensure system meets minimum requirements
2. **Review Logs:** Look for error messages in terminal output
3. **Enable Debug Mode:** Set `FIB_DEBUG=true` for detailed logging
4. **Consult Documentation:** Check troubleshooting section
5. **Search Issues:** Look for similar problems in GitHub issues
6. **Report Bugs:** Create new issue with installation details and error messages

**Information to include in bug reports:**
- Operating system and version
- Python version (`python --version`)
- Installation method used
- Complete error messages
- Steps to reproduce the issue
