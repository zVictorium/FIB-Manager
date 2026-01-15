# API Reference

Technical documentation for FIB Manager's internal modules and the UPC FIB API integration.

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [UPC FIB API](#upc-fib-api)
- [Module Reference](#module-reference)
- [Data Structures](#data-structures)
- [Schedule Generation Algorithm](#schedule-generation-algorithm)
- [Extending FIB Manager](#extending-fib-manager)

---

## Architecture Overview

FIB Manager follows a modular architecture:

```
src/app/
├── __main__.py          # Entry point
├── __version__.py       # Version info
├── api/
│   └── api.py           # FIB API client
├── commands/
│   ├── command_line.py  # CLI argument parsing
│   ├── search.py        # Schedule search command
│   ├── subjects.py      # Subjects list command
│   └── marks.py         # Grade calculator command
├── core/
│   ├── constants.py     # Configuration constants
│   ├── parser.py        # Data parsing utilities
│   ├── schedule_generator.py  # Schedule algorithm
│   ├── utils.py         # Helper functions
│   └── validator.py     # Schedule validation
└── ui/
    ├── interactive.py   # Interactive mode
    └── ui.py            # UI components
```

---

## UPC FIB API

FIB Manager uses the official UPC FIB Public API.

### Base URL

```
https://api.fib.upc.edu/v2
```

### Authentication

The API uses a client ID for authentication:
```
client_id=77qvbbQqni4TcEUsWvUCKOG1XU7Hr0EfIs4pacRz
```

### Endpoints Used

#### Classes Data

Get class schedules for a quadrimester:

```
GET /quadrimestres/{quadrimester}/classes.json
```

**Parameters:**
- `quadrimester`: Quadrimester code (e.g., `2025Q1`)
- `client_id`: API client ID
- `lang`: Language code (`en`, `es`, `ca`)

**Response:**
```json
{
  "count": 150,
  "next": "https://api.fib.upc.edu/v2/.../classes.json?page=2",
  "results": [
    {
      "codi_assig": "IES",
      "grup": "10",
      "dia_setmana": 1,
      "inici": "09:00",
      "dupinici": 540,
      "final": "11:00",
      "duracio": 2,
      "tipus": "T",
      "idioma": "English"
    }
  ]
}
```

#### Subjects List

Get all subject information:

```
GET /assignatures.json
```

**Parameters:**
- `client_id`: API client ID
- `format`: Response format (`json`)
- `lang`: Language code

**Response:**
```json
{
  "count": 100,
  "results": [
    {
      "id": "IES",
      "nom": "Interacció i Sistemes",
      "credits": 6.0
    }
  ]
}
```

### Pagination

The API uses pagination. FIB Manager handles this automatically by following the `next` URL until all data is retrieved.

---

## Module Reference

### api.api

HTTP client for the FIB API.

#### `get_json_response(url: str, language: str) -> Dict`

Make a GET request and return JSON.

```python
from app.api import get_json_response

data = get_json_response(
    "https://api.fib.upc.edu/v2/assignatures.json",
    "en"
)
```

#### `get_paginated_data(base_url: str, language: str) -> List`

Fetch all pages from a paginated endpoint.

```python
from app.api import get_paginated_data

all_classes = get_paginated_data(
    "https://api.fib.upc.edu/v2/quadrimestres/2025Q1/classes.json",
    "en"
)
```

#### `fetch_classes_data(quadrimester: str, language: str) -> Dict`

Fetch class data for a specific quadrimester.

```python
from app.api import fetch_classes_data

data = fetch_classes_data("2025Q1", "en")
```

#### `fetch_subject_names(language: str) -> Dict[str, str]`

Fetch mapping of subject codes to names.

```python
from app.api import fetch_subject_names

names = fetch_subject_names("en")
# {'IES': 'Interacció i Sistemes', 'XC': 'Xarxes de Computadors', ...}
```

### core.schedule_generator

Schedule combination generator.

#### `get_schedule_combinations(...) -> Dict`

Generate all valid schedule combinations.

```python
from app.core.schedule_generator import get_schedule_combinations

result = get_schedule_combinations(
    quadrimester="2025Q1",
    subjects=["IES", "XC"],
    start_hour=9,
    end_hour=18,
    languages=["en", "es"],
    require_matching_subgroup=True,
    relax_days=0,
    blacklist=[],
    max_dead_hours=-1,
    show_progress=True,
    sort_mode="groups"
)
```

**Returns:**
```python
{
    "quad": "2025Q1",
    "start": 9,
    "end": 18,
    "subjects": ["IES", "XC"],
    "total": 42,
    "schedules": [...]
}
```

### core.parser

Data parsing utilities.

#### `parse_classes_data(raw_data: Dict) -> Dict`

Parse raw API data into organized structure.

```python
from app.core.parser import parse_classes_data

parsed = parse_classes_data(raw_api_response)
# {
#     "IES": {
#         "10": [...],  # Theory group
#         "11": [...]   # Lab group
#     }
# }
```

#### `split_schedule_by_group_type(parsed_data: Dict) -> Tuple`

Separate theory groups from lab groups.

```python
from app.core.parser import split_schedule_by_group_type

groups, subgroups = split_schedule_by_group_type(parsed_data)
```

### core.validator

Schedule validation and merging.

#### `get_valid_combinations(...) -> List`

Find all non-conflicting group combinations.

#### `merge_valid_schedules(...) -> Tuple[List, List]`

Merge group and subgroup combinations into complete schedules.

### commands.marks

Grade calculation utilities.

#### `find_variable_names(formula: str) -> List[str]`

Extract variable names from a formula.

```python
from app.commands.marks import find_variable_names

vars = find_variable_names("EX1*0.6 + EX2*0.4")
# ['EX1', 'EX2']
```

#### `process_marks_calculation(formula, values, target)`

Solve for unknown variables in a grading formula.

---

## Data Structures

### Schedule Object

```python
{
    "subjects": {
        "IES": {
            "group": 10,
            "subgroup": 11
        },
        "XC": {
            "group": 20,
            "subgroup": 21
        }
    },
    "url": "https://www.fib.upc.edu/...",
    "days": 4,
    "dead_hours": 2
}
```

### Class Entry

```python
{
    "subject": "IES",
    "group": "10",
    "day": 1,              # Monday = 1, Friday = 5
    "start": 9,            # Hour (9:00)
    "end": 11,             # Hour (11:00)
    "duration": 2,         # Hours
    "type": "T",           # T=Theory, L=Lab, P=Problems
    "language": "English"
}
```

### Parsed Schedule Structure

```python
{
    "IES": {
        "10": [  # Group 10 (Theory)
            {"day": 1, "start": 9, "end": 11, "type": "T", "language": "English"},
            {"day": 3, "start": 9, "end": 11, "type": "T", "language": "English"}
        ],
        "11": [  # Group 11 (Lab)
            {"day": 2, "start": 11, "end": 13, "type": "L", "language": "English"}
        ]
    }
}
```

---

## Schedule Generation Algorithm

FIB Manager uses an optimized algorithm for schedule generation:

### 1. Data Fetching
```
Fetch class data from API → Parse into structured format
```

### 2. Constraint Filtering
```
Filter classes by:
- Time constraints (start/end hours)
- Language preferences
- Blacklisted groups
```

### 3. Combination Generation
```
For each subject:
    Get valid theory groups
    Get valid lab groups
Generate Cartesian product of all combinations
```

### 4. Conflict Detection
```
For each combination:
    Check for time slot overlaps
    Validate max days constraint
    Calculate dead hours
    Skip if exceeds max_dead_hours
```

### 5. Sorting and Output
```
Sort by number of groups or dead hours
Return top results
```

### Performance Optimizations

- **Precomputed slot caching**: Time slots are cached for fast overlap detection
- **Early pruning**: Invalid combinations are rejected early
- **Set-based conflict detection**: O(1) conflict checks using slot sets

---

## Extending FIB Manager

### Adding a New Command

1. Create a new module in `commands/`:

```python
# commands/mycommand.py
from argparse import ArgumentParser, Namespace

def add_mycommand_arguments(parser: ArgumentParser) -> None:
    parser.add_argument("--option", help="My option")

def handle_mycommand(args: Namespace) -> None:
    print(f"Running mycommand with {args.option}")
```

2. Register in `command_line.py`:

```python
from app.commands.mycommand import add_mycommand_arguments, handle_mycommand

# In build_argument_parser():
mycommand_parser = subparsers.add_parser("mycommand", help="My command")
add_mycommand_arguments(mycommand_parser)

# In main():
elif args.command == "mycommand":
    handle_mycommand(args)
```

### Adding API Endpoints

Add new functions to `api/api.py`:

```python
def fetch_custom_data(param: str) -> Dict:
    url = f"{API_BASE_URL}/custom/{param}.json?client_id={CLIENT_ID}"
    return get_paginated_data(url, "en")
```

---

**← [Interactive Mode](Interactive-Mode.md)** | **[FAQ →](FAQ.md)**
