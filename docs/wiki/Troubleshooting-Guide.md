# Troubleshooting Guide

Comprehensive troubleshooting guide for common issues and solutions when using FIB Manager.

## Installation Issues

### Python-Related Problems

#### Problem: "Python not found" or "'python' is not recognized"

**Symptoms:**
```cmd
python --version
'python' is not recognized as an internal or external command
```

**Solutions:**

1. **Install Python:**
   - Download from [python.org](https://python.org/downloads/)
   - During installation, check "Add Python to PATH"
   - Verify: `python --version`

2. **Fix PATH Environment Variable:**
   ```cmd
   REM Add Python to PATH manually
   set PATH=%PATH%;C:\Python312;C:\Python312\Scripts
   
   REM Or find Python location
   where python
   ```

3. **Use Alternative Commands:**
   ```cmd
   REM Try python3 instead of python
   python3 --version
   
   REM Or use full path
   C:\Python312\python.exe --version
   ```

#### Problem: "pip not found" or pip installation errors

**Symptoms:**
```cmd
pip install -r requirements.txt
'pip' is not recognized as an internal or external command
```

**Solutions:**

1. **Install pip:**
   ```cmd
   REM Download get-pip.py and run
   python get-pip.py
   
   REM Or reinstall Python with pip included
   ```

2. **Use python -m pip:**
   ```cmd
   REM Use module execution instead
   python -m pip install -r requirements.txt
   python -m pip install -e .
   ```

3. **Fix pip PATH:**
   ```cmd
   REM Add Scripts directory to PATH
   set PATH=%PATH%;C:\Python312\Scripts
   ```

#### Problem: Virtual environment creation fails

**Symptoms:**
```cmd
python -m venv .venv
Error: No module named venv
```

**Solutions:**

1. **Install venv module:**
   ```cmd
   REM For Ubuntu/Debian
   sudo apt install python3-venv
   
   REM For CentOS/RHEL
   sudo dnf install python3-venv
   ```

2. **Use alternative methods:**
   ```cmd
   REM Use virtualenv instead
   pip install virtualenv
   virtualenv .venv
   
   REM Or use conda
   conda create -n fib-manager python=3.12
   conda activate fib-manager
   ```

3. **Check Python installation:**
   ```cmd
   REM Verify complete Python installation
   python -c "import venv; print('venv available')"
   ```

### Dependency Issues

#### Problem: Package installation failures

**Symptoms:**
```cmd
pip install -r requirements.txt
ERROR: Could not find a version that satisfies the requirement...
```

**Solutions:**

1. **Update pip and setuptools:**
   ```cmd
   python -m pip install --upgrade pip setuptools wheel
   ```

2. **Clear pip cache:**
   ```cmd
   pip cache purge
   pip install -r requirements.txt --no-cache-dir
   ```

3. **Use specific package versions:**
   ```cmd
   REM Install compatible versions manually
   pip install requests>=2.25.0
   pip install rich>=12.0.0
   pip install questionary>=1.10.0
   ```

4. **Check Python version compatibility:**
   ```cmd
   python --version
   REM Ensure Python 3.8 or higher
   ```

#### Problem: "Microsoft Visual C++ required" (Windows)

**Symptoms:**
```
error: Microsoft Visual C++ 14.0 is required
```

**Solutions:**

1. **Install Visual Studio Build Tools:**
   - Download from Microsoft website
   - Install "C++ build tools" workload
   - Restart command prompt

2. **Use pre-compiled wheels:**
   ```cmd
   pip install --only-binary=all -r requirements.txt
   ```

3. **Alternative: Use conda:**
   ```cmd
   conda install -c conda-forge package-name
   ```

### Permission Issues

#### Problem: "Permission denied" errors

**Symptoms:**
```cmd
pip install -e .
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**Solutions:**

1. **Use virtual environment (recommended):**
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   pip install -e .
   ```

2. **Install to user directory:**
   ```cmd
   pip install --user -e .
   ```

3. **Run as administrator (not recommended):**
   ```cmd
   REM Right-click Command Prompt -> "Run as administrator"
   pip install -e .
   ```

## Runtime Issues

### API Connection Problems

#### Problem: "Failed to fetch data: HTTP 500"

**Symptoms:**
```cmd
fib-manager subjects
Error: Failed to fetch data: HTTP 500
```

**Diagnostic Steps:**

1. **Check API status:**
   ```cmd
   REM Test basic connectivity
   ping raco.fib.upc.edu
   
   REM Test HTTP response
   curl -I https://raco.fib.upc.edu/api/
   ```

**Solutions:**

1. **Retry after delay:**
   ```cmd
   REM Wait and try again (temporary server issues)
   timeout /t 60
   fib-manager subjects
   ```

2. **Try different quadrimester:**
   ```cmd
   REM Test with known working quadrimester
   fib-manager subjects -q 2024Q1
   ```

3. **Check internet connection:**
   ```cmd
   REM Test general connectivity
   ping google.com
   nslookup raco.fib.upc.edu
   ```

#### Problem: "Connection timeout" or "Network unreachable"

**Symptoms:**
```cmd
fib-manager subjects
Error: Connection timeout
```

**Solutions:**

1. **Check firewall settings:**
   - Ensure FIB Manager is allowed through firewall
   - Check corporate firewall restrictions
   - Verify HTTPS (port 443) is open

2. **Configure proxy (if applicable):**
   ```cmd
   set HTTP_PROXY=http://proxy.server:port
   set HTTPS_PROXY=http://proxy.server:port
   fib-manager subjects
   ```

3. **Use alternative network:**
   ```cmd
   REM Try different network connection
   REM Use mobile hotspot or different WiFi
   ```

### Data and Parsing Issues

#### Problem: "Invalid quadrimester format"

**Symptoms:**
```cmd
fib-manager subjects -q 24Q1
Error: Invalid quadrimester format
```

**Solutions:**

1. **Use correct format:**
   ```cmd
   REM Correct format: YYYYQ[1-2]
   fib-manager subjects -q 2024Q1
   fib-manager subjects -q 2024Q2
   ```

2. **Check available quadrimesters:**
   ```cmd
   REM Let system auto-detect
   fib-manager subjects
   ```

3. **Verify current academic year:**
   ```cmd
   REM Use current or recent year
   fib-manager subjects -q 2024Q2
   ```

#### Problem: "Subject not found: XYZ"

**Symptoms:**
```cmd
fib-manager schedules -s IES XC INVALID
Error: Subject not found: INVALID
```

**Solutions:**

1. **List available subjects:**
   ```cmd
   fib-manager subjects -q 2024Q1
   fib-manager subjects -v
   ```

2. **Check subject code format:**
   ```cmd
   REM Use uppercase subject codes
   fib-manager schedules -s IES XC PROP
   
   REM Not lowercase
   REM fib-manager schedules -s ies xc prop
   ```

3. **Verify quadrimester availability:**
   ```cmd
   REM Some subjects only available in specific quadrimesters
   fib-manager subjects -q 2024Q1 | findstr "SUBJECTCODE"
   fib-manager subjects -q 2024Q2 | findstr "SUBJECTCODE"
   ```

### Schedule Generation Issues

#### Problem: "No schedules found"

**Symptoms:**
```cmd
fib-manager schedules -s IES XC PROP BD
{
  "total_schedules": 0,
  "schedules": []
}
```

**Diagnostic Steps:**

1. **Test with fewer subjects:**
   ```cmd
   fib-manager schedules -s IES XC
   ```

2. **Check individual subjects:**
   ```cmd
   fib-manager schedules -s IES
   fib-manager schedules -s XC
   fib-manager schedules -s PROP
   ```

3. **Identify constraint conflicts:**
   ```cmd
   REM Remove constraints one by one
   fib-manager schedules -s IES XC PROP BD --days 5
   fib-manager schedules -s IES XC PROP BD --start 8 --end 20
   fib-manager schedules -s IES XC PROP BD
   ```

**Solutions:**

1. **Relax time constraints:**
   ```cmd
   REM Expand time window
   fib-manager schedules -s IES XC PROP --start 8 --end 20
   ```

2. **Increase day limit:**
   ```cmd
   REM Allow more days
   fib-manager schedules -s IES XC PROP --days 5
   ```

3. **Allow subgroup flexibility:**
   ```cmd
   REM Enable freedom mode
   fib-manager schedules -s IES XC PROP --freedom
   ```

4. **Remove language restrictions:**
   ```cmd
   REM Accept any language
   fib-manager schedules -s IES XC PROP
   ```

#### Problem: Schedule generation takes too long

**Symptoms:**
```cmd
fib-manager schedules -s IES XC PROP BD SO ASO
REM Command hangs for several minutes
```

**Solutions:**

1. **Reduce number of subjects:**
   ```cmd
   REM Process subjects in smaller groups
   fib-manager schedules -s IES XC PROP
   fib-manager schedules -s BD SO ASO
   ```

2. **Add constraints to reduce complexity:**
   ```cmd
   REM Limit combinations with constraints
   fib-manager schedules -s IES XC PROP BD SO ^
     --days 4 ^
     --max-dead-hours 3 ^
     --start 9 --end 18
   ```

3. **Use different sorting:**
   ```cmd
   REM Groups sorting is typically faster
   fib-manager schedules -s IES XC PROP BD --sort groups
   ```

### Interactive Mode Issues

#### Problem: Interactive mode doesn't work

**Symptoms:**
```cmd
fib-manager app
Error: Interactive mode not supported on this terminal
```

**Solutions:**

1. **Use modern terminal:**
   ```cmd
   REM Windows: Use Windows Terminal or PowerShell
   REM Avoid Command Prompt for interactive mode
   powershell
   fib-manager app
   ```

2. **Check terminal capabilities:**
   ```cmd
   REM Test ANSI color support
   echo [31mRed Text[0m
   ```

3. **Use CLI mode instead:**
   ```cmd
   REM Use command-line interface
   fib-manager schedules -s IES XC -v
   fib-manager subjects -v
   ```

#### Problem: Keyboard navigation doesn't work

**Symptoms:**
- Arrow keys don't navigate menus
- Enter key doesn't select options
- Interface appears frozen

**Solutions:**

1. **Check terminal settings:**
   - Ensure terminal supports keyboard input
   - Disable conflicting key bindings
   - Try different terminal application

2. **Alternative input methods:**
   ```cmd
   REM Try number keys instead of arrows
   REM Type option names instead of navigating
   ```

3. **Restart application:**
   ```cmd
   REM Exit with Ctrl+C and restart
   fib-manager app
   ```

## Command-Line Issues

### Argument Parsing Problems

#### Problem: "Unrecognized arguments"

**Symptoms:**
```cmd
fib-manager schedules -s IES XC --invalid-option
error: unrecognized arguments: --invalid-option
```

**Solutions:**

1. **Check available options:**
   ```cmd
   fib-manager schedules --help
   fib-manager subjects --help
   fib-manager marks --help
   ```

2. **Verify option spelling:**
   ```cmd
   REM Correct option names
   fib-manager schedules -s IES XC --freedom
   fib-manager schedules -s IES XC --blacklist IES-101
   ```

3. **Check option format:**
   ```cmd
   REM Some options require values
   fib-manager schedules -s IES XC --start 9
   fib-manager schedules -s IES XC --languages en es
   ```

#### Problem: "Required arguments missing"

**Symptoms:**
```cmd
fib-manager schedules
error: the following arguments are required: -s/--subjects
```

**Solutions:**

1. **Provide required arguments:**
   ```cmd
   REM Subjects are required for schedules command
   fib-manager schedules -s IES XC
   ```

2. **Check command syntax:**
   ```cmd
   fib-manager schedules --help
   ```

3. **Use correct argument format:**
   ```cmd
   REM Multiple subjects
   fib-manager schedules -s IES XC PROP
   
   REM Multiple languages
   fib-manager schedules -s IES XC -l en es
   ```

### Output and Display Issues

#### Problem: Garbled or missing output

**Symptoms:**
- Special characters display incorrectly
- Colors don't appear
- Tables are malformed

**Solutions:**

1. **Set console encoding:**
   ```cmd
   REM Set UTF-8 encoding
   chcp 65001
   fib-manager subjects
   ```

2. **Use different terminal:**
   ```cmd
   REM Windows Terminal supports Unicode better
   wt
   fib-manager subjects -v
   ```

3. **Disable colors (if needed):**
   ```cmd
   REM Force plain text output
   set NO_COLOR=1
   fib-manager subjects
   ```

#### Problem: JSON output is malformed

**Symptoms:**
```cmd
fib-manager schedules -s IES XC
{Invalid JSON output...
```

**Solutions:**

1. **Check for error messages:**
   ```cmd
   REM Look for error output in terminal
   fib-manager schedules -s IES XC
   ```

2. **Validate JSON:**
   ```cmd
   REM Pipe to jq for validation
   fib-manager schedules -s IES XC | jq .
   ```

3. **Use interactive mode:**
   ```cmd
   REM Alternative to JSON output
   fib-manager schedules -s IES XC -v
   ```

## Grade Calculator Issues

### Formula Problems

#### Problem: "Invalid formula syntax"

**Symptoms:**
```cmd
fib-manager marks --formula "EX1 + EX2 +" --target 7.0
Error: Invalid formula syntax
```

**Solutions:**

1. **Check formula syntax:**
   ```cmd
   REM Valid formulas
   fib-manager marks --formula "EX1 + EX2" --target 7.0
   fib-manager marks --formula "EX1*0.4 + EX2*0.6" --target 7.0
   fib-manager marks --formula "max(EX1, EX2)" --target 7.0
   ```

2. **Use proper operators:**
   ```cmd
   REM Supported operators: + - * / ^ ( )
   REM Supported functions: min, max, round, abs
   fib-manager marks --formula "round((EX1 + EX2)/2)" --target 7.0
   ```

3. **Avoid unsupported features:**
   ```cmd
   REM Don't use: = (use == for comparison)
   REM Don't use: ** (use ^ for exponentiation)
   REM Don't use: // (use / for division)
   ```

#### Problem: "Unknown variable" or formula evaluation errors

**Symptoms:**
```cmd
fib-manager marks --formula "EX1 + UNKNOWN" --target 7.0 --values EX1=5.0
Error: Unknown variable: UNKNOWN
```

**Solutions:**

1. **Provide all variable values:**
   ```cmd
   fib-manager marks --formula "EX1 + EX2" --target 7.0 --values EX1=5.0 EX2=6.0
   ```

2. **Check variable names:**
   ```cmd
   REM Variables are case-sensitive
   fib-manager marks --formula "EX1 + EX2" --target 7.0 --values EX1=5.0
   REM Not: ex1=5.0
   ```

3. **Use consistent naming:**
   ```cmd
   REM Match variable names exactly
   fib-manager marks --formula "MIDTERM*0.5 + FINAL*0.5" --target 7.0 --values MIDTERM=6.0
   ```

## Performance Issues

### Slow Performance

#### Problem: Commands take a long time to execute

**Symptoms:**
- API calls timeout
- Schedule generation is very slow
- Application appears frozen

**Solutions:**

1. **Check network connection:**
   ```cmd
   REM Test network speed
   ping -t raco.fib.upc.edu
   ```

2. **Reduce complexity:**
   ```cmd
   REM Use fewer subjects
   fib-manager schedules -s IES XC  REM Instead of 8+ subjects
   
   REM Add constraints
   fib-manager schedules -s IES XC PROP --days 4 --max-dead-hours 3
   ```

3. **Use specific parameters:**
   ```cmd
   REM Avoid auto-detection
   fib-manager schedules -s IES XC -q 2024Q1
   ```

#### Problem: High memory usage

**Symptoms:**
- System becomes slow
- "Out of memory" errors
- Application crashes

**Solutions:**

1. **Process subjects in batches:**
   ```cmd
   REM Split large requests
   fib-manager schedules -s IES XC PROP > batch1.json
   fib-manager schedules -s BD SO ASO > batch2.json
   ```

2. **Add memory constraints:**
   ```cmd
   REM Limit dead hours to reduce combinations
   fib-manager schedules -s IES XC PROP BD --max-dead-hours 2
   ```

3. **Close other applications:**
   ```cmd
   REM Free up system memory before running
   ```

## Environment and System Issues

### Windows-Specific Issues

#### Problem: Script execution policy (PowerShell)

**Symptoms:**
```powershell
.\scripts\setup.bat
Execution of scripts is disabled on this system
```

**Solutions:**

1. **Change execution policy:**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   .\scripts\setup.bat
   ```

2. **Use Command Prompt instead:**
   ```cmd
   REM Run from cmd.exe instead of PowerShell
   scripts\setup.bat
   ```

#### Problem: Long path issues

**Symptoms:**
```cmd
Error: The filename or extension is too long
```

**Solutions:**

1. **Enable long paths:**
   ```cmd
   REM Run as administrator
   reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1
   ```

2. **Use shorter paths:**
   ```cmd
   REM Move project to shorter path
   C:\fib-manager\
   ```

### Path and Environment Issues

#### Problem: Environment variables not recognized

**Symptoms:**
```cmd
set FIB_DEBUG=true
fib-manager subjects
REM Debug mode doesn't activate
```

**Solutions:**

1. **Verify environment variable:**
   ```cmd
   echo %FIB_DEBUG%
   ```

2. **Set in current session:**
   ```cmd
   set FIB_DEBUG=true
   fib-manager subjects
   ```

3. **Set permanently:**
   ```cmd
   setx FIB_DEBUG true
   REM Restart command prompt
   ```

## Getting Help and Support

### Diagnostic Information

When reporting issues, include:

1. **System Information:**
   ```cmd
   REM Operating system
   ver
   
   REM Python version
   python --version
   
   REM FIB Manager version
   fib-manager --version
   ```

2. **Error Details:**
   ```cmd
   REM Command that failed
   fib-manager command-that-fails
   ```

3. **Environment Setup:**
   ```cmd
   REM Virtual environment status
   echo %VIRTUAL_ENV%
   
   REM Installed packages
   pip list
   ```

### Community Support

1. **GitHub Issues:** Report bugs with detailed information
2. **Discussions:** Ask questions and share experiences
3. **Wiki:** Check documentation for additional guidance
4. **Stack Overflow:** Search for similar problems

### Creating Effective Bug Reports

Include these elements:

1. **Clear Description:** What you expected vs what happened
2. **Reproduction Steps:** Exact commands that cause the issue
3. **Environment Details:** OS, Python version, installation method
4. **Error Messages:** Complete error output with debug enabled
5. **Workarounds:** Any temporary solutions you've tried

### Quick Fixes Summary

**Most Common Solutions:**

1. **Restart with clean environment:**
   ```cmd
   deactivate
   python -m venv fresh-env
   fresh-env\Scripts\activate
   pip install -e .
   ```

2. **Update dependencies:**
   ```cmd
   pip install --upgrade pip
   pip install -r requirements.txt --upgrade
   ```

3. **Clear caches:**
   ```cmd
   pip cache purge
   ```

4. **Test basic connectivity:**
   ```cmd
   fib-manager subjects
   ```
