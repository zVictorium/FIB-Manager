# FAQ & Troubleshooting

Frequently asked questions and solutions to common problems.

## 📋 Table of Contents

- [General Questions](#general-questions)
- [Installation Issues](#installation-issues)
- [Schedule Search Problems](#schedule-search-problems)
- [Interactive Mode Issues](#interactive-mode-issues)
- [API and Connection](#api-and-connection)
- [Grade Calculator](#grade-calculator)
- [Getting Help](#getting-help)

---

## General Questions

### What is FIB Manager?

FIB Manager is a tool for FIB (Facultat d'Informàtica de Barcelona - UPC) students that helps generate valid class schedules, browse subjects, and calculate grades using the official UPC API.

### Is FIB Manager official?

No, FIB Manager is an unofficial tool created by students for students. It uses the official public UPC FIB API but is not affiliated with or endorsed by UPC.

### What data does FIB Manager use?

FIB Manager fetches real-time data from the UPC FIB API:
- Class schedules and times
- Available groups and languages
- Subject names and codes

### Does FIB Manager store my data?

No, FIB Manager does not store any personal data. All searches are performed locally and data is fetched fresh from the API each time.

### What languages are supported?

The application interface is in English. Class information can be displayed in:
- English (en)
- Spanish/Castellano (es)
- Catalan/Català (ca)

---

## Installation Issues

### "Python not found" or "python is not recognized"

**Problem**: Python is not in your system PATH.

**Solution**:
1. Reinstall Python from [python.org](https://www.python.org/downloads/)
2. Check "Add Python to PATH" during installation
3. Restart your terminal

### "pip not found"

**Problem**: pip is not installed or not in PATH.

**Solution**:
```bash
# Try using python -m pip instead
python -m pip install -r requirements.txt

# Or reinstall pip
python -m ensurepip --upgrade
```

### "Module not found: rich" (or other modules)

**Problem**: Dependencies are not installed.

**Solution**:
```bash
pip install -r requirements.txt

# Or install individually
pip install rich questionary pyfiglet requests tqdm
```

### Permission denied errors on Linux/macOS

**Problem**: Insufficient permissions.

**Solution**:
```bash
# Use --user flag
pip install --user -r requirements.txt

# Or use sudo (not recommended)
sudo pip install -r requirements.txt
```

### Windows SmartScreen blocks the executable

**Problem**: Windows doesn't recognize the publisher.

**Solution**:
1. Click "More info"
2. Click "Run anyway"

This is normal for unsigned applications.

---

## Schedule Search Problems

### "No schedules found"

**Possible causes**:
1. **Too many constraints**: Try relaxing some options
2. **Subject not available**: Check if the subject is offered in that quadrimester
3. **Language filter too strict**: Add more languages

**Solutions**:
```bash
# Remove language filter
fib-manager schedules -s IES XC

# Extend time range
fib-manager schedules -s IES XC --start 8 --end 21

# Increase max days
fib-manager schedules -s IES XC --days 5

# Remove dead hours limit
fib-manager schedules -s IES XC --max-dead-hours -1
```

### "Subject code not found"

**Problem**: Invalid subject code.

**Solution**:
1. Use the subjects command to list valid codes:
   ```bash
   fib-manager subjects -q 2025Q1
   ```
2. Subject codes are case-insensitive but must be exact

### Search is very slow

**Possible causes**:
1. Too many subjects selected
2. API response is slow

**Solutions**:
- Reduce number of subjects
- Add more constraints to filter combinations early
- Check your internet connection

### Schedules have time conflicts

**Problem**: This should not happen with FIB Manager.

**Solution**: Please report this as a bug on [GitHub Issues](https://github.com/zvictorium/fib-manager/issues).

---

## Interactive Mode Issues

### Colors/characters display incorrectly

**Problem**: Terminal doesn't support Unicode or ANSI colors.

**Solutions**:
1. **Windows**: Use Windows Terminal instead of cmd.exe
2. **Linux/macOS**: Ensure terminal supports UTF-8
3. Set terminal encoding:
   ```bash
   export LANG=en_US.UTF-8
   ```

### Arrow keys don't work

**Problem**: Terminal input mode issue.

**Solutions**:
1. Try a different terminal emulator
2. On Windows, use PowerShell or Windows Terminal
3. Check if your SSH connection supports arrow keys

### Screen doesn't clear properly

**Problem**: Terminal clear command compatibility.

**Solution**: Try running in a different terminal or resize the window.

### Interactive mode crashes immediately

**Problem**: Missing UI dependencies.

**Solution**:
```bash
pip install rich questionary pyfiglet --force-reinstall
```

---

## API and Connection

### "Failed to fetch data" or connection errors

**Possible causes**:
1. No internet connection
2. API is down
3. Firewall blocking requests

**Solutions**:
1. Check internet connection
2. Verify API is accessible:
   ```bash
   curl https://api.fib.upc.edu/v2/
   ```
3. Check firewall/proxy settings

### "HTTP 429 Too Many Requests"

**Problem**: Rate limiting from the API.

**Solution**: Wait a few minutes and try again. Avoid making many rapid requests.

### Outdated schedule data

**Problem**: API data might not be up to date.

**Note**: FIB Manager fetches data directly from the UPC API. If data seems outdated, it's because the official source hasn't been updated yet.

---

## Grade Calculator

### "Error: You must specify --formula and --target"

**Problem**: Missing required arguments.

**Solution**:
```bash
fib-manager marks --formula "EX1*0.6+EX2*0.4" --target 5.0
```

### Formula parsing errors

**Problem**: Invalid formula syntax.

**Common mistakes**:
- Using `x` for multiplication (use `*`)
- Missing operators between terms
- Unbalanced parentheses

**Examples**:
```bash
# Wrong
fib-manager marks --formula "EX1 x 0.6"

# Correct
fib-manager marks --formula "EX1*0.6"
```

### "No solution found"

**Problem**: Mathematically impossible to reach target.

**Example**: Target is 10 but formula has maximum possible value of 8.

### Variable names not recognized

**Problem**: Using reserved function names as variables.

**Reserved names**: `min`, `max`, `round`, `abs`, `sum`, `pow`

**Solution**: Use different variable names (e.g., `NOTA_MAX` instead of `max`).

---

## Getting Help

### Report a Bug

1. Go to [GitHub Issues](https://github.com/zvictorium/fib-manager/issues)
2. Click "New Issue"
3. Include:
   - FIB Manager version
   - Operating system
   - Steps to reproduce
   - Error messages
   - Command used

### Request a Feature

1. Go to [GitHub Issues](https://github.com/zvictorium/fib-manager/issues)
2. Click "New Issue"
3. Describe the feature you'd like

### Contact

- **GitHub**: [zvictorium/fib-manager](https://github.com/zvictorium/fib-manager)
- **Issues**: [Report bugs](https://github.com/zvictorium/fib-manager/issues)

---

## Quick Reference

### Command Cheat Sheet

```bash
# Start interactive mode
fib-manager app

# Basic schedule search
fib-manager schedules -s IES XC

# Full schedule search
fib-manager schedules -q 2025Q1 -s IES XC PROP \
  --start 9 --end 18 -l en es --days 4 -v

# List subjects
fib-manager subjects -q 2025Q1 -l en

# Grade calculation
fib-manager marks --formula "EX1*0.6+EX2*0.4" --target 7.0
```

### Quadrimester Format

- **2025Q1**: First quadrimester of 2025 (September - January)
- **2025Q2**: Second quadrimester of 2025 (February - June)

### Language Codes

| Input | Accepted variants |
|-------|-------------------|
| English | `en`, `english`, `anglés`, `angles` |
| Spanish | `es`, `spanish`, `español`, `castellano` |
| Catalan | `ca`, `catalan`, `català`, `catala` |

---

**← [API Reference](API-Reference.md)** | **[Home](Home.md)**
