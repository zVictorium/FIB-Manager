# Schedule Searcher CLI

A command-line tool to search and generate valid class schedules for FIB degrees using the UPC public API.

## Features

- Fetches class data for a given quadrimester
- Generates valid group and subgroup timetable combinations
- Filters by time range, languages, blacklisted groups, and relax days
- Outputs results in JSON and provides direct timetable URLs

## Requirements

- Python 3.8 or higher
- requests (see requirements.txt)

## Installation

### Windows

```bat
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
```

### Linux / macOS

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Usage

Invoke subcommands:

```bash
fib-horarios commands                   # show all subcommands and flags
fib-horarios search --subjects SUBJ1 SUBJ2 [OPTIONS]  # search schedules
fib-horarios subjects [OPTIONS]         # list available subjects
```

## Common Options

# Global and subcommand-specific Options

-- `--quad`: Quadrimester code (e.g., `YYYYQ1` or `YYYYQ2`; defaults to current quad based on date)
-- `--subjects`: List of subject codes (required for `search`)
-- `--start-hour`: Start hour inclusive (default `8`)
-- `--end-hour`: End hour exclusive (default `20`)
-- `--languages`: Preferred class languages (`en`, `es`, `ca`, default: all)
-- `--same-subgroup-as-group`: Require subgroup tens match group
-- `--relax-days`: Number of relaxable off-days (default `0`)
-- `--blacklisted`: Blacklisted subject-group pairs (e.g., `IES-101`)
-- `--lang`: Language code for subject names and API (e.g., `en`, `es`, `ca`; default `en`)
-- `--debug`: Enable debug output

### Examples

```bash
python runner.py search --quad 2024Q2 --subjects IES-101 FIB-202 --start-hour 9 --end-hour 18 --languages en es --relax-days 1
```

The command will print matching timetable combinations in JSON, including a `url` field for each schedule.

## Contributing

1. Fork the repository and clone locally
2. Create a new branch for your feature or fix
3. Commit your changes and push to your fork
4. Open a pull request against the `main` branch

## License

This project is licensed under the MIT License.
