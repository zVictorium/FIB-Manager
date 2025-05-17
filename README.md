# Schedule Searcher CLI

A command-line tool to search and generate valid class schedules for FIB degrees using the UPC public API.

## Features

- Fetches class data for a given quadrimester
- Generates valid group and subgroup timetable combinations
- Filters by time range, languages, blacklisted groups, and days
- Outputs results in JSON format
- Interactive schedule visualization with grid view
- Provides direct timetable URLs with one-click opening
- Built-in subject browser with search capabilities
- Full interactive mode with guided parameter selection

## Requirements

- Python 3.8 or higher
- Python packages:
  - requests
  - rich
  - pyfiglet
  - questionary
  - (see requirements.txt for full list)

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

The tool can be used either through the command line interface or in fully interactive mode.

### CLI Mode

```bash
fib-manager <command> [OPTIONS]
```

Available commands:

```bash
fib-manager app                   # Start the interactive application
fib-manager schedules --subjects SUBJ1 SUBJ2 [OPTIONS]  # Search schedules
fib-manager subjects [OPTIONS]    # List available subjects
```

### Interactive Mode

```bash
fib-manager app
```

This launches a fully interactive application where you can:
- Browse available subjects for any quadrimester
- Select subjects, time constraints, languages, and other preferences through menus
- View and navigate through compatible schedules in a visual interface
- Open schedule URLs directly in your browser with a single keypress

## Command Options

### Global Options

- `-q`, `--quadrimester`: Quadrimester code (e.g., `2023Q1` or `2023Q2`; defaults to current quad based on date)
- `--debug`: Enable debug output

### Schedules Command Options

- `-s`, `--subjects`: List of subject codes (required)
- `--start`: Start hour inclusive (default `8`)
- `--end`: End hour exclusive (default `20`)
- `-l`, `--languages`: Preferred class languages (`en`, `es`, `ca`, default: all)
- `--freedom`: Allow different subgroup tens than group (flag, no value required)
- `--days`: Maximum number of days with classes (default `5`)
- `--blacklist`: Blacklisted subject-group pairs (e.g., `IES-101`)
- `-v`, `--view`: Display results in interactive interface (flag, no value required)

### Subjects Command Options

- `-q`, `--quadrimester`: Quadrimester code (e.g., `2023Q1`)
- `-l`, `--language`: Language code for subject names (e.g., `en`, `es`, `ca`; default `en`)
- `-v`, `--view`: Display subjects in interactive interface (flag, no value required)

## Examples

### Searching for schedule combinations

```bash
fib-manager schedules --quadrimester 2024Q2 -s IES-101 FIB-202 --start 9 --end 18 -l en es --days 4 --freedom
```

The command will print matching timetable combinations in JSON format.

### Using the interactive interface

```bash
fib-manager schedules -s IES-101 FIB-202 -v
```

This opens the interactive schedule browser where you can:
- Navigate between valid schedules with arrow keys
- Switch between schedule grid and group list views with TAB
- Open the current schedule in a browser with SPACE
- Quit the application with Q or return to command mode with ESC

### Listing available subjects

```bash
fib-manager subjects -q 2024Q1 -l en
```

Lists all subjects available in the specified quadrimester in JSON format.

```bash
fib-manager subjects -q 2024Q1 -v
```

Displays subjects in an interactive table format.

## Interactive Mode Keys

When viewing schedules in the interactive interface:
- `←` / `→`: Navigate between schedules
- `SPACE`: Open current schedule URL in browser
- `TAB`: Toggle between grid view and group list
- `ESC`: Return to previous menu
- `Q`: Quit application

## Contributing

1. Fork the repository and clone locally
2. Create a new branch for your feature or fix
3. Commit your changes and push to your fork
4. Open a pull request against the `main` branch

## License

This project is licensed under the MIT License.
