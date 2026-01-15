# Interactive Mode Guide

Learn how to use FIB Manager's interactive console application for the best user experience.

## 📋 Table of Contents

- [Starting Interactive Mode](#starting-interactive-mode)
- [Main Menu](#main-menu)
- [Schedule Search Wizard](#schedule-search-wizard)
- [Schedule Browser](#schedule-browser)
- [Subject Explorer](#subject-explorer)
- [Grade Calculator](#grade-calculator)
- [Navigation Controls](#navigation-controls)

---

## Starting Interactive Mode

Launch the interactive application:

```bash
fib-manager app
```

Or using Python directly:
```bash
python -m app app
```

You'll be greeted with a splash screen displaying the FIB Manager logo and version information.

---

## Main Menu

The main menu provides access to all features:

```
╔════════════════════════════════╗
║       FIB MANAGER              ║
╠════════════════════════════════╣
║  [1] Schedule Search           ║
║  [2] Browse Subjects           ║
║  [3] Grade Calculator (Beta)   ║
║  [4] Exit                      ║
╚════════════════════════════════╝
```

Use the arrow keys (↑↓) to navigate and **Enter** to select.

---

## Schedule Search Wizard

The schedule search wizard guides you through setting up your search parameters step by step.

### Step 1: Select Year

Choose the academic year:
- Previous year
- Current year
- Next year

### Step 2: Select Quadrimester

Choose which quadrimester:
- **1** (September - January)
- **2** (February - June)

### Step 3: Set Time Constraints

**Start hour**: When you want your classes to begin (8-20)
- Example: Select `9` if you don't want classes before 9:00 AM

**End hour**: When your classes should end (start+1 to 21)
- Example: Select `18` if you want to be free after 6:00 PM

### Step 4: Maximum Days

Set how many days per week you want classes:
- `1` to `5` days
- Default is `5` (all weekdays)

### Step 5: Subgroup Freedom

**"Allow different subgroup than group?"**
- **No** (default): Your lab/subgroup matches your theory group
- **Yes**: More flexibility but potentially inconsistent groups

### Step 6: Language Preferences

Select which class languages to include:
- ☐ English
- ☐ Spanish  
- ☐ Catalan

Use **Space** to toggle selections, **Enter** to confirm.

> **Note**: At least one language must be selected.

### Step 7: Select Subjects

Browse and select the subjects you want to include:

```
Select subjects:
  [x] PROP - Projecte de Programació
  [ ] XC - Xarxes de Computadors
  [x] IES - Interacció i Sistemes
  [ ] EDA - Estructures de Dades
```

- Use **↑↓** to navigate
- Use **Space** to toggle selection
- Type to search/filter subjects
- Press **Enter** when done

### Step 8: Blacklist Groups (Optional)

If you want to exclude specific groups:

```
Blacklisted groups:
  [ ] IES-10
  [ ] IES-20
  [ ] XC-10
```

Leave empty and press **Enter** to skip.

### Step 9: Dead Hours Limit

Set maximum "dead hours" (gaps between classes):
- **No limit**: Allow any gaps
- **0**: No gaps allowed
- **1-5**: Maximum hours of gaps per day

---

## Schedule Browser

After search completes, view results in the schedule browser.

### Schedule Grid View

```
╔════════════════════════════════════════════════════════════════╗
║  Schedule 1 of 42                                              ║
╠════════════════════════════════════════════════════════════════╣
║ Hour │ Monday    │ Tuesday   │ Wednesday │ Thursday  │ Friday  ║
╠══════╪═══════════╪═══════════╪═══════════╪═══════════╪═════════╣
║  8   │           │           │           │           │         ║
║  9   │ IES-10T   │           │ XC-20T    │           │         ║
║ 10   │ IES-10T   │           │ XC-20T    │           │         ║
║ 11   │           │ PROP-11L  │           │ IES-11L   │         ║
║ 12   │           │ PROP-11L  │           │ IES-11L   │         ║
║ ...  │           │           │           │           │         ║
╚════════════════════════════════════════════════════════════════╝
```

### Information Panel

Below the grid, see:
- Total classes and hours per week
- Number of different groups
- Total dead hours
- Days with classes

### Navigation

| Key | Action |
|-----|--------|
| `←` / `→` | Previous / Next schedule |
| `↑` / `↓` | Scroll within schedule |
| `Home` | Go to first schedule |
| `End` | Go to last schedule |
| `q` | Return to main menu |

### Color Coding

Each subject is assigned a unique color for easy identification:
- Theory classes (T)
- Lab classes (L)
- Problems classes (P)

---

## Subject Explorer

Browse all available subjects for a quadrimester.

### Interface

```
╔══════════════════════════════════════════════════════╗
║  Subjects - 2025Q1 (English)                         ║
╠══════════════════════════════════════════════════════╣
║  Code  │ Name                                        ║
╠════════╪═════════════════════════════════════════════╣
║  AC    │ Arquitectura de Computadors                 ║
║  ADA   │ Algorítmica i Disseny d'Algorismes          ║
║  BD    │ Bases de Dades                              ║
║  ...   │ ...                                         ║
╚══════════════════════════════════════════════════════╝
```

### Steps

1. Select **Year**
2. Select **Quadrimester**
3. Select **Language** for subject names

---

## Grade Calculator

Calculate grades using mathematical formulas (Beta feature).

### Interface

1. **Enter Formula**: Type your grading formula
   ```
   Formula: EX1*0.6 + EX2*0.4
   ```

2. **Enter Target**: Your desired final grade
   ```
   Target grade: 7.0
   ```

3. **Enter Known Values**: Grades you already have
   ```
   Known values (VAR=VALUE, empty to finish):
   EX1=8.0
   ```

4. **View Results**: See what you need on remaining exams

### Formula Examples

| Description | Formula |
|-------------|---------|
| Simple weighted average | `EX1*0.6 + EX2*0.4` |
| With minimum | `max(LAB*0.3, EXAM*0.7)` |
| Multiple components | `P1*0.2 + P2*0.2 + FINAL*0.6` |
| Conditional | `(LAB>5)*LAB*0.3 + EXAM*0.7` |

### Supported Functions

- `min(a, b)` - Minimum of values
- `max(a, b)` - Maximum of values
- `abs(x)` - Absolute value
- `round(x)` - Round to nearest integer
- `sum(a, b, c, ...)` - Sum of values
- `pow(base, exp)` - Exponentiation

---

## Navigation Controls

### Global Controls

| Key | Action |
|-----|--------|
| **Enter** | Confirm selection |
| **↑↓** | Navigate options |
| **Space** | Toggle checkbox |
| **Esc** or **q** | Go back / Exit |
| **Ctrl+C** | Force exit |

### Selection Lists

| Key | Action |
|-----|--------|
| Type | Filter/search items |
| **Space** | Toggle selection (checkboxes) |
| **Enter** | Confirm selection |

### Schedule Viewer

| Key | Action |
|-----|--------|
| **←→** | Navigate schedules |
| **↑↓** | Scroll view |
| **Home/End** | First/last schedule |
| **o** | Open schedule URL in browser |
| **q** | Exit viewer |

---

## Tips for Best Experience

### Terminal Size

For optimal display, use a terminal window that is:
- At least 120 characters wide
- At least 30 lines tall

### Windows Users

For best results on Windows:
- Use Windows Terminal (recommended)
- Or PowerShell with a modern font
- Enable Unicode support

### Quick Workflow

1. Launch with `fib-manager app`
2. Select "Schedule Search"
3. Use default values for quick setup
4. Browse results with arrow keys
5. Press `o` to open your favorite in a browser

---

**← [Commands Reference](Commands.md)** | **[API Reference →](API-Reference.md)**
