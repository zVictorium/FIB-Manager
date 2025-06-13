# CLI Reference

Complete reference for all FIB Manager command-line interface commands and options.

## Global Options

These options are available for all commands:

| Option | Description | Example |
|--------|-------------|---------|
| `-q, --quadrimester` | Quadrimester code (auto-detected if not specified) | `-q 2024Q1` |
| `-h, --help` | Show help message | `--help` |
| `--version` | Show version information | `--version` |

## Commands Overview

FIB Manager provides four main commands:

1. **`app`** - Start the interactive application
2. **`schedules`** - Generate and filter schedule combinations
3. **`subjects`** - List and browse available subjects
4. **`marks`** - Calculate grades and solve formulas (Beta)

## Command: `app`

Start the interactive console application with a guided interface.

### Syntax
```bash
fib-manager app
```

### Description
Launches the full interactive application that provides:
- Subject browser with search functionality
- Guided schedule generation setup
- Visual schedule viewer with keyboard navigation
- Interactive grade calculator
- Multi-language support

### Requirements
- Windows terminal with ANSI color support (Windows Terminal, PowerShell)
- Keyboard input support for navigation
- Internet connection for API access

### Examples
```bash
# Start interactive mode
fib-manager app
```

---

## Command: `schedules`

Generate and filter valid schedule combinations for selected subjects.

### Syntax
```bash
fib-manager schedules -s SUBJECT1 SUBJECT2 [OPTIONS]
```

### Required Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `-s, --subjects` | List of subject codes | `-s IES XC PROP` |

### Optional Arguments

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-q, --quadrimester` | String | Auto-detected | Quadrimester code (e.g., 2024Q1) |
| `--start` | Integer | `8` | Starting hour (inclusive, 24h format) |
| `--end` | Integer | `20` | Ending hour (exclusive, 24h format) |
| `-l, --languages` | List | All | Preferred languages (`en`, `es`, `ca`) |
| `--freedom` | Flag | `False` | Allow different subgroup tens than group |
| `--days` | Integer | `5` | Maximum number of days with classes |
| `--blacklist` | List | - | Blacklisted subject-group pairs |
| `--max-dead-hours` | Integer | `-1` | Maximum dead hours allowed (-1 for no limit) |
| `--sort` | String | `groups` | Sort mode: `groups` or `dead-hours` |
| `-v, --view` | Flag | `False` | Launch interactive schedule viewer |

### Output Format

**JSON Output (default):**
```json
{
  "quadrimester": "2024Q1",
  "subjects": ["IES", "XC"],
  "total_schedules": 12,
  "schedules": [
    {
      "id": 1,
      "subjects": {
        "IES": {"group": 101, "subgroup": 111},
        "XC": {"group": 201, "subgroup": 211}
      },
      "dead_hours": 2,
      "url": "https://raco.fib.upc.edu/...",
      "sessions": [...]
    }
  ]
}
```

### Examples

**Basic Usage:**
```bash
# Simple schedule search
fib-manager schedules -s IES XC

# With time constraints
fib-manager schedules -s IES XC --start 9 --end 18

# Prefer specific languages
fib-manager schedules -s IES XC PROP -l en es
```

**Advanced Filtering:**
```bash
# Blacklist specific groups
fib-manager schedules -s IES XC --blacklist IES-101 XC-205

# Allow flexible subgroup assignment
fib-manager schedules -s IES XC --freedom

# Limit dead hours and maximum days
fib-manager schedules -s IES XC --max-dead-hours 2 --days 4
```

**Interactive Mode:**
```bash
# View results in interactive interface
fib-manager schedules -s IES XC PROP --sort dead-hours -v
```

---

## Command: `subjects`

List and browse available subjects for a specific quadrimester.

### Syntax
```bash
fib-manager subjects [OPTIONS]
```

### Optional Arguments

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-q, --quadrimester` | String | Auto-detected | Quadrimester code |
| `-l, --language` | String | `en` | Display language (`en`, `es`, `ca`) |
| `-v, --view` | Flag | `False` | Interactive table viewer |

### Output Format

**JSON Output (default):**
```json
{
  "quadrimester": "2024Q1",
  "language": "en",
  "subjects": {
    "IES": "Software Engineering",
    "XC": "Computer Networks",
    "PROP": "Programming Project"
  }
}
```

### Examples

```bash
# List all subjects for current quadrimester
fib-manager subjects

# Specific quadrimester in Spanish
fib-manager subjects -q 2024Q1 -l es

# Interactive subject browser
fib-manager subjects -v

# Catalan subject names for 2024Q2
fib-manager subjects -q 2024Q2 -l ca
```

---

## Command: `marks` (Beta)

Advanced grade calculation and formula solving for academic planning.

### Syntax
```bash
fib-manager marks --formula "FORMULA" --target TARGET [OPTIONS]
```

### Required Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `--formula` | Mathematical formula with variables | `"EX1*0.4+EX2*0.6"` |
| `--target` | Target grade to achieve | `7.0` |

### Optional Arguments

| Option | Type | Description |
|--------|------|-------------|
| `--values` | List | Known variable values in format `VAR=value` |
| `-v, --view` | Flag | Interactive results viewer |

### Formula Syntax

**Variables:**
- Use any alphanumeric name (e.g., `EX1`, `LAB`, `FINAL`, `MIDTERM`)
- Case-sensitive
- No spaces in variable names

**Operators:**
- `+` Addition
- `-` Subtraction  
- `*` Multiplication
- `/` Division
- `^` Exponentiation
- `()` Parentheses for grouping

**Functions:**
- `min(a, b, ...)` - Minimum value
- `max(a, b, ...)` - Maximum value
- `round(x)` - Round to nearest integer
- `abs(x)` - Absolute value

**Comparison Operators:**
- `>` Greater than
- `<` Less than
- `>=` Greater than or equal
- `<=` Less than or equal
- `==` Equal to
- `!=` Not equal to

### Output Format

**JSON Output (default):**
```json
{
  "formula": "EX1*0.4+EX2*0.6",
  "target": 7.0,
  "known_values": {"EX1": 6.5},
  "missing_variables": ["EX2"],
  "solution": {"EX2": 7.33},
  "result": 7.0
}
```

### Examples

**Basic Calculations:**
```bash
# Calculate needed final exam grade
fib-manager marks \
  --formula "LAB*0.3 + MIDTERM*0.3 + FINAL*0.4" \
  --target 7.0 \
  --values LAB=8.5 MIDTERM=6.0

# Simple two-exam formula
fib-manager marks \
  --formula "EX1*0.6 + EX2*0.4" \
  --target 5.0 \
  --values EX1=4.0
```

**Complex Formulas:**
```bash
# Formula with conditions
fib-manager marks \
  --formula "max(0.4*EX1 + 0.6*EX2, min(EX1, EX2))" \
  --target 5.0 \
  --values EX1=4.0

# Multiple variables
fib-manager marks \
  --formula "round((LAB + PROJ + EXAM)/3)" \
  --target 8 \
  --values LAB=7.5 PROJ=9.0
```

**Interactive Mode:**
```bash
# Launch interactive grade calculator
fib-manager marks --view
```

---

## Error Handling

### Common Exit Codes

| Code | Description |
|------|-------------|
| `0` | Success |
| `1` | General error |
| `2` | Invalid arguments |
| `3` | API connection error |
| `4` | Data parsing error |
| `5` | Interactive mode not supported |

### Error Messages

**API Errors:**
- `"Failed to fetch data: HTTP 500"` - API server error
- `"Connection timeout"` - Network connectivity issues
- `"Invalid quadrimester format"` - Malformed quadrimester code

**Validation Errors:**
- `"Subject not found: XYZ"` - Subject code doesn't exist
- `"Invalid time range"` - Start hour >= end hour
- `"No schedules found"` - No valid combinations exist

**Formula Errors:**
- `"Invalid formula syntax"` - Malformed mathematical expression
- `"Unknown variable: VAR"` - Variable not defined in formula
- `"Division by zero"` - Mathematical error in formula

---

## Environment Variables

FIB Manager supports these environment variables for configuration:

| Variable | Description | Default |
|----------|-------------|---------|
| `FIB_API_BASE_URL` | Override default API base URL | UPC official API |
| `FIB_DEFAULT_LANGUAGE` | Default language for API requests | `en` |
| `FIB_CACHE_TIMEOUT` | API response cache timeout (seconds) | `300` |
| `FIB_DEBUG` | Enable debug logging | `false` |

### Example
```bash
# Windows
set FIB_DEBUG=true
fib-manager subjects

# Linux/macOS  
export FIB_DEBUG=true
fib-manager subjects
```

---

## Output Redirection

All commands support standard output redirection:

```bash
# Save JSON output to file
fib-manager subjects > subjects.json

# Pipe to other tools
fib-manager schedules -s IES XC | jq '.total_schedules'

# Append to log file
fib-manager schedules -s IES XC >> schedules.log 2>&1
```

---

## Performance Tips

1. **Use specific quadrimester codes** instead of auto-detection for faster responses
2. **Limit subject count** to 10 or fewer for optimal performance  
3. **Enable caching** by reusing the same terminal session
4. **Use blacklists** to reduce computation time for large result sets
5. **Avoid very broad time ranges** (e.g., 8-22) when possible
