# Commands Reference

Complete reference for all FIB Manager command-line interface commands.

## 📋 Table of Contents

- [Overview](#overview)
- [Global Usage](#global-usage)
- [app Command](#app-command)
- [schedules Command](#schedules-command)
- [subjects Command](#subjects-command)
- [marks Command](#marks-command)
- [Output Formats](#output-formats)

---

## Overview

FIB Manager provides four main commands:

| Command | Description |
|---------|-------------|
| `app` | Launch the interactive application |
| `schedules` | Search and generate schedule combinations |
| `subjects` | List available subjects for a quadrimester |
| `marks` | Calculate and analyze academic grades |

---

## Global Usage

```bash
fib-manager <command> [options]
```

To see help for any command:

```bash
fib-manager --help
fib-manager <command> --help
```

---

## app Command

Launch the interactive console application.

### Usage

```bash
fib-manager app
```

### Description

Starts the full interactive application with menus for:
- Schedule search and browsing
- Subject exploration
- Grade calculation

No additional arguments are needed. See [Interactive Mode Guide](Interactive-Mode.md) for details.

---

## schedules Command

Search for valid schedule combinations based on your constraints.

### Usage

```bash
fib-manager schedules -s <subjects> [options]
```

### Required Arguments

| Argument | Description |
|----------|-------------|
| `-s`, `--subjects` | List of subject codes (space-separated) |

### Optional Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `-q`, `--quadrimester` | Current | Quadrimester code (e.g., `2025Q1`) |
| `--start` | `8` | Start hour (inclusive, 8-20) |
| `--end` | `20` | End hour (exclusive, 9-21) |
| `-l`, `--languages` | All | Preferred languages (`en`, `es`, `ca`) |
| `--freedom` | Off | Allow different subgroup than group |
| `--days` | `5` | Maximum days with classes (1-5) |
| `--blacklist` | None | Groups to exclude (e.g., `IES-10`) |
| `--whitelist` | None | Groups that must be included (e.g., `IES-10`) |
| `--max-dead-hours` | `-1` | Maximum dead hours (-1 = no limit) |
| `--sort` | `groups` | Sort by `groups` or `dead_hours` |
| `-v`, `--view` | Off | Show results in interactive viewer |

### Examples

**Basic schedule search:**
```bash
fib-manager schedules -s IES XC
```

**Search with time constraints:**
```bash
fib-manager schedules -s IES XC PROP --start 9 --end 18
```

**Search for specific languages only:**
```bash
fib-manager schedules -s IES XC -l en es
```

**Limit to 4 days maximum:**
```bash
fib-manager schedules -s IES XC PROP EDA --days 4
```

**Blacklist specific groups:**
```bash
fib-manager schedules -s IES XC --blacklist IES-10 XC-20
```

**Whitelist groups that must be included:**
```bash
fib-manager schedules -s IES XC FM --whitelist IES-10 FM-11
```

**Combine blacklist and whitelist:**
```bash
fib-manager schedules -s IES XC FM --blacklist IES-20 --whitelist FM-11
```

**Limit dead hours:**
```bash
fib-manager schedules -s IES XC PROP --max-dead-hours 2
```

**Allow flexible subgroups:**
```bash
fib-manager schedules -s IES XC --freedom
```

**View results interactively:**
```bash
fib-manager schedules -s IES XC -v
```

**Complete example:**
```bash
fib-manager schedules \
  -q 2025Q2 \
  -s IES XC PROP EDA \
  --start 9 \
  --end 19 \
  -l en \
  --days 4 \
  --max-dead-hours 2 \
  --blacklist IES-10 \
  --whitelist XC-11 \
  --sort dead_hours \
  -v
```

### Output

Returns JSON with:
- `quad`: Quadrimester code
- `start`, `end`: Hour range
- `subjects`: Requested subjects
- `total`: Number of valid schedules found
- `schedules`: Array of schedule objects

---

## subjects Command

List all available subjects for a quadrimester.

### Usage

```bash
fib-manager subjects [options]
```

### Optional Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `-q`, `--quadrimester` | Current | Quadrimester code (e.g., `2025Q1`) |
| `-l`, `--language` | `en` | Language for subject names |
| `-v`, `--view` | Off | Show in interactive viewer |

### Examples

**List subjects for current quadrimester:**
```bash
fib-manager subjects
```

**List subjects in Spanish:**
```bash
fib-manager subjects -l es
```

**List subjects for specific quadrimester:**
```bash
fib-manager subjects -q 2025Q2
```

**View interactively:**
```bash
fib-manager subjects -q 2025Q1 -l en -v
```

### Output

Returns JSON with:
- `quadrimester`: Quadrimester code
- `language`: Language used
- `subjects`: Object mapping subject codes to names

---

## marks Command

Calculate grades using mathematical formulas.

### Usage

```bash
fib-manager marks --formula <formula> --target <value> [options]
```

### Required Arguments

| Argument | Description |
|----------|-------------|
| `--formula` | Mathematical formula with variables |
| `--target` | Target result value |

### Optional Arguments

| Argument | Description |
|----------|-------------|
| `--values` | Known values in `VAR=VALUE` format |
| `-v`, `--view` | Show results in interactive viewer |

### Formula Syntax

Formulas support:
- Basic arithmetic: `+`, `-`, `*`, `/`
- Exponentiation: `^` or `**`
- Parentheses for grouping
- Variables: Any alphanumeric identifier
- Functions: `min()`, `max()`, `round()`, `abs()`, `sum()`, `pow()`

### Examples

**Basic grade calculation:**
```bash
fib-manager marks --formula "EX1*0.6+EX2*0.4" --target 7.0
```

**With known values:**
```bash
fib-manager marks \
  --formula "EX1*0.6+EX2*0.4" \
  --target 7.0 \
  --values EX1=8.0
```

**Complex formula:**
```bash
fib-manager marks \
  --formula "max(LAB*0.3, min(EX1, EX2)*0.3) + FINAL*0.7" \
  --target 5.0 \
  --values LAB=7.5 EX1=6.0
```

**View results interactively:**
```bash
fib-manager marks --formula "P1*0.4+P2*0.6" --target 5.0 -v
```

### Output

Returns JSON with:
- `formula`: The input formula
- `target`: Target value
- `values`: All variable values (known and solved)
- `solution`: Calculated solution for unknown variable

---

## Output Formats

### JSON Output (Default)

All commands output JSON by default, suitable for:
- Piping to other tools (`jq`, etc.)
- Integration with scripts
- Programmatic processing

```bash
fib-manager subjects -q 2025Q1 | jq '.subjects | keys'
```

### Interactive View (-v flag)

Add `-v` or `--view` to any command to display results in an interactive terminal interface with:
- Visual schedule grids
- Navigation controls
- Color-coded information

---

## Tips

### Quadrimester Format

Quadrimester codes follow the format `YYYYQN`:
- `YYYY`: Year (e.g., 2025)
- `Q`: Literal "Q"
- `N`: Quadrimester number (1 or 2)

Example: `2025Q1`, `2025Q2`

### Subject Codes

Subject codes are case-insensitive. Common examples:
- `IES` - Interacció i Sistemes
- `XC` - Xarxes de Computadors
- `PROP` - Projecte de Programació
- `EDA` - Estructures de Dades i Algorismes

### Language Codes

| Code | Language |
|------|----------|
| `en` | English |
| `es` | Spanish (Castellano) |
| `ca` | Catalan |

---

**← [Installation](Installation.md)** | **[Interactive Mode →](Interactive-Mode.md)**
