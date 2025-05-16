import logging
import os
import sys
import atexit
import webbrowser
import json
from datetime import date
from argparse import ArgumentParser, Namespace

try:
    import msvcrt
except ImportError:
    msvcrt = None

from rich.console import Console
from rich.table import Table
from rich import box
from rich.theme import Theme
from rich.text import Text
from rich.align import Align
from pyfiglet import figlet_format
import questionary
from questionary import Style as QStyle

from app.scheduler import (
    get_schedule_combinations,
    fetch_classes_data,
    parse_classes_data,
    fetch_subject_names,
)

# Constants
LANGUAGE_MAP = {
    "catala": "ca", "català": "ca", "catalan": "ca", "ca": "ca",
    "castella": "es", "castellà": "es", "castellano": "es", 
    "espanol": "es", "español": "es", "spanish": "es", "es": "es",
    "english": "en", "anglés": "en", "angles": "en", 
    "inglés": "en", "ingles": "en", "en": "en",
}

LANG_FLAGS = {"en": "ENG", "es": "ESP", "ca": "CAT"}

UI_THEME = Theme({
    "primary": "white",
    "secondary": "bright_black",
    "accent": "red",
    "warning": "bold red",
    "error": "bold red",
})

QUESTIONARY_STYLE = QStyle([
    ("qmark", "fg:#FF5555 bold"),       # light red
    ("question", "fg:#FFFFFF"),         # white
    ("answer", "fg:#AAAAAA"),           # light gray
    ("pointer", "fg:#666666 bold"),     # gray
    ("highlighted", "fg:#FF5555 bold"), # light red
    ("selected", "fg:#AAAAAA"),         # light gray
    ("separator", "fg:#AAAAAA"),        # light gray
    ("instruction", "fg:#AAAAAA"),      # light gray
    ("text", "fg:#AAAAAA"),             # light gray
])

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
SHORT_WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
SUBJECT_COLORS = [
    "#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", 
    "#BAE1FF", "#FFECB3", "#D7BDE2", "#AED6F1",
]

console = Console(theme=UI_THEME)

# Ensure cursor is shown on program exit
atexit.register(lambda: print("\033[?25h", end="", flush=True))


def get_default_quadrimester() -> str:
    """Compute default quadrimester based on current date."""
    today = date.today()
    half = 1 if today.month <= 6 else 2
    return f"{today.year-1}Q{half+1}"


def normalize_language(language_code: str) -> str:
    """Normalize language code to standard format."""
    return LANGUAGE_MAP.get(language_code.lower(), language_code)


def normalize_languages(languages: list[str]) -> list[str]:
    """Normalize a list of language codes."""
    return [normalize_language(lang) for lang in languages]


def parse_blacklisted_pairs(items: list[str]) -> list[list[str, int]]:
    """Parse blacklisted subject-group strings into lists."""
    result = []
    
    for item in items:
        if "-" not in item:
            continue
            
        subject, group = item.split("-", 1)
        if not group.isdigit():
            continue
            
        result.append([subject, int(group)])
        
    return result


def setup_argument_parser(default_quad: str) -> ArgumentParser:
    parser = ArgumentParser(prog="fib-manager")
    subparsers = parser.add_subparsers(dest="command")

    # App command
    subparsers.add_parser("app", help="Start enhanced interactive application")

    # Search command
    search_parser = subparsers.add_parser(
        "search", help="Search for schedule combinations"
    )
    _add_search_arguments(search_parser, default_quad)

    # Subjects command
    subjects_parser = subparsers.add_parser(
        "subjects", help="Show all available subjects for a quad"
    )
    _add_subjects_arguments(subjects_parser, default_quad)

    return parser


def _add_search_arguments(parser: ArgumentParser, default_quad: str) -> None:
    """Add common arguments to search and interface parsers."""
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--quad", default=default_quad, 
                        help=f"Quadrimester code, e.g., {default_quad}")
    parser.add_argument("--subjects", nargs="+", required=True, 
                        help="List of subject codes")
    parser.add_argument("--start-hour", type=int, default=8, 
                        help="Start hour (inclusive)")
    parser.add_argument("--end-hour", type=int, default=20, 
                        help="End hour (exclusive)")
    parser.add_argument("--languages", nargs="*", default=[], 
                        help="Preferred class languages")
    parser.add_argument("--same-subgroup-as-group", action="store_true",
                        help="Require subgroup tens match group")
    parser.add_argument("--relax-days", type=int, default=0, 
                        help="Number of relaxable off-days")
    parser.add_argument("--blacklisted", nargs="*", default=[],
                        help="Blacklisted subject-group pairs, e.g., IES-101")
    parser.add_argument("--interface", action="store_true",
                        help="Show search results in interactive interface")


def _add_subjects_arguments(parser: ArgumentParser, default_quad: str) -> None:
    """Add --quad and --lang args to the 'subjects' subparser."""
    parser.add_argument(
        "-q", "--quad",
        default=default_quad,
        help=f"Quadrimester code, e.g., {default_quad}"
    )
    parser.add_argument(
        "-l", "--lang",
        default="en",
        help="Language code for subject names (e.g., en, es, ca)"
    )
    parser.add_argument(
        "-i", "--interface",
        action="store_true",
        help="Display subjects in interactive interface (default: JSON output)"
    )


def configure_debug_mode(debug_enabled: bool) -> None:
    """Configure debug mode if enabled."""
    if not debug_enabled:
        return
        
    logging.basicConfig(level=logging.DEBUG)
    import app.scheduler as sched
    sched.DEBUG = True


def handle_search_command(args: Namespace) -> None:
    """Process the 'search' command."""
    configure_debug_mode(args.debug)

    # Normalize languages
    args.languages = normalize_languages(args.languages)
    args.blacklisted = parse_blacklisted_pairs(args.blacklisted)
    
    # Convert subjects to uppercase
    args.subjects = [subject.upper() for subject in args.subjects]
    
    # Fetch data
    raw_classes = fetch_classes_data(args.quad, "en")
    parsed_classes = parse_classes_data(raw_classes)
    
    # Get schedule combinations
    result = get_schedule_combinations(
        args.quad,
        args.subjects,
        args.start_hour,
        args.end_hour,
        args.languages,
        args.same_subgroup_as_group,
        args.relax_days,
        args.blacklisted,
        args.interface
    )
    
    # Use the interface if requested
    if args.interface:
        show_interactive_interface(result, parsed_classes, args.start_hour, args.end_hour)
    else:
        # Display results as plain JSON
        print(json.dumps(result, indent=2))


def show_interactive_interface(result: dict, parsed_classes: dict, start_hour: int, end_hour: int) -> None:
    """Show search results in an interactive interface."""
    hide_cursor()
    
    if not check_windows_platform():
        return
    
    schedules = result.get("schedules", [])
    if not schedules:
        console.print("No schedules found to display.", style="error", justify="center")
        show_cursor()
        return
    
    # Navigate through schedules
    navigate_schedules(schedules, parsed_classes, start_hour, end_hour)
    
    clear_screen()
    show_cursor()


def hide_cursor() -> None:
    """Hide the terminal cursor."""
    print("\033[?25l", end="", flush=True)


def show_cursor() -> None:
    """Show the terminal cursor."""
    print("\033[?25h", end="", flush=True)


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def check_windows_platform() -> bool:
    """Check if running on Windows platform and msvcrt is available."""
    if msvcrt is None:
        console.print(
            "Interactive mode is only supported on Windows.",
            style="error",
            justify="center",
        )
        show_cursor()
        return False
    return True


def create_subject_color_map(schedules: list[dict]) -> dict:
    """Create a map of subjects to colors for consistent rendering."""
    all_subjects = set()
    
    for schedule in schedules:
        all_subjects.update(schedule.get("subjects", {}).keys())
    
    return {
        subject: SUBJECT_COLORS[i % len(SUBJECT_COLORS)] 
        for i, subject in enumerate(sorted(all_subjects))
    }


def display_schedule_grid(
    schedule: dict, 
    parsed_classes: dict,
    start_hour: int, 
    end_hour: int,
    subject_colors: dict
) -> Table:
    """Create a grid table displaying the schedule."""
    grid = {}
    subjects_info = schedule.get("subjects", {})
    
    # Collect class information
    for subject, info in subjects_info.items():
        for group_type in ("group", "subgroup"):
            group = info.get(group_type)
            if not group:
                continue
                
            for class_info in parsed_classes.get(subject, {}).get(str(group), []):
                key = (class_info["day"], class_info["hour"])
                grid.setdefault(key, []).append((subject, class_info, info))
    
    # Create table
    grid_table = Table(
        show_lines=True,
        title="Schedule",
        box=box.SIMPLE_HEAVY,
        header_style="secondary",
    )
    
    # Add columns
    grid_table.add_column(justify="right", header_style="bold")
    for day in WEEKDAYS:
        grid_table.add_column(day, style="accent", header_style="bold", justify="center")
    
    # Add rows
    for hour in range(start_hour, end_hour):
        row = [str(hour)]
        
        for day_index in range(len(WEEKDAYS)):
            entries = grid.get((day_index + 1, hour), [])
            cell = Text()
            
            for subject, class_info, info in entries:
                class_type = class_info.get("type", "")
                type_letter = class_type[0].upper() if class_type else ""
                
                # Format language flags
                flags = []
                for lang in class_info.get("language", "").split(","):
                    lang_code = normalize_language(lang.lower())
                    flag = LANG_FLAGS.get(lang_code, "")
                    if flag:
                        flags.append(flag)
                flag_text = " ".join(flags)
                
                # Determine which group to show
                group = (
                    info["group"]
                    if class_info in parsed_classes.get(subject, {}).get(str(info["group"]), [])
                    else info["subgroup"]
                )
                
                # Format cell content
                classroom = class_info.get("classroom", "").replace(",", "")
                line = f"{subject} {group}{type_letter}\n{classroom}\n{flag_text}"
                cell.append(line, style=subject_colors.get(subject, "primary"))
                
            row.append(cell)
            
        grid_table.add_row(*row)
        
    return grid_table


def display_subject_table(schedule: dict, subject_colors: dict) -> Table:
    """Create a table displaying subject and group information."""
    table = Table(title="Subjects and groups", header_style="secondary")
    
    # Add columns
    table.add_column("Subject", justify="center", header_style="bold")
    table.add_column("Group", justify="center", header_style="bold")
    table.add_column("Subgroup", justify="center", header_style="bold")
    
    # Add rows
    for subject, info in schedule.get("subjects", {}).items():
        subject_style = subject_colors.get(subject, "primary")
        
        table.add_row(
            Text(subject, style=subject_style),
            Text(str(info.get("group", "")), style=subject_style),
            Text(str(info.get("subgroup", "")), style=subject_style),
        )
        
    return table


def display_interface_schedule(
    index: int, 
    total: int,
    schedules: list[dict],
    parsed_classes: dict,
    start_hour: int,
    end_hour: int,
    subject_colors: dict,
    show_grid: bool
) -> None:
    """Display a schedule in the interface."""
    clear_screen()
    schedule = schedules[index]
    
    # Check if schedule contains any subjects
    if not schedule.get("subjects"):
        console.print(
            "No sessions available for this schedule.",
            style="warning",
            justify="center",
        )
        console.print(
            "Use ←→ to navigate, q to quit",
            style="warning",
            justify="center",
        )
        return
    
    # Display header with schedule number
    header = (
        Text("Schedule ", style="white") +
        Text(str(index + 1), style="#FF5555") +
        Text("/", style="bright_black") +
        Text(str(total), style="#FF5555")
    )
    console.rule(header, style="accent")
    console.print()
    console.print()
    
    # Display appropriate view based on setting
    if show_grid:
        grid_table = display_schedule_grid(
            schedule, parsed_classes, start_hour, end_hour, subject_colors
        )
        console.print(grid_table, justify="center")
    else:
        subject_table = display_subject_table(schedule, subject_colors)
        console.print(subject_table, justify="center")
    
    # Display navigation instructions
    console.print()
    console.print()
    console.print(
        "Press SPACE to open schedule URL",
        style="primary",
        justify="center",
    )
    
    view_text = "Press TAB to show groups" if show_grid else "Press TAB to show schedule"
    console.print(view_text, style="primary", justify="center")
    
    console.print()
    console.print("←→ to navigate", style="warning", justify="center")
    console.print()
    console.print("Q to quit\nESC to leave", style="accent", justify="center")


def navigate_schedules(
    schedules: list[dict],
    parsed_classes: dict,
    start_hour: int,
    end_hour: int
) -> None:
    """Interactive schedule navigation."""
    if not schedules:
        console.print("No schedules found.", style="error", justify="center")
        clear_screen()
        return
        
    total_schedules = len(schedules)
    current_index = 0
    show_grid = True
    subject_colors = create_subject_color_map(schedules)
    
    display_interface_schedule(
        current_index, 
        total_schedules,
        schedules, 
        parsed_classes,
        start_hour,
        end_hour,
        subject_colors,
        show_grid
    )
    
    while True:
        key = msvcrt.getwch()
        
        if key == " ":
            # Open schedule URL in browser
            webbrowser.open(schedules[current_index]["url"])
        elif key == "\t":
            # Toggle between grid and group views
            show_grid = not show_grid
            display_interface_schedule(
                current_index, 
                total_schedules,
                schedules, 
                parsed_classes,
                start_hour,
                end_hour,
                subject_colors,
                show_grid
            )
        elif key == "\xe0":  # Arrow keys
            code = msvcrt.getwch()
            if code == "M":  # Right arrow
                current_index = (current_index + 1) % total_schedules
                display_interface_schedule(
                    current_index, 
                    total_schedules,
                    schedules, 
                    parsed_classes,
                    start_hour,
                    end_hour,
                    subject_colors,
                    show_grid
                )
            elif code == "K":  # Left arrow
                current_index = (current_index - 1) % total_schedules
                display_interface_schedule(
                    current_index, 
                    total_schedules,
                    schedules, 
                    parsed_classes,
                    start_hour,
                    end_hour,
                    subject_colors,
                    show_grid
                )
        elif key.lower() == "q":
            show_cursor()
            sys.exit(0)
        elif key == "\x1b":  # ESC
            break
            
    clear_screen()


def display_legacy_interface_schedule(
    index: int,
    schedules: list[dict],
    parsed_classes: dict,
    start_hour: int,
    end_hour: int
) -> None:
    """Display a schedule in the legacy interface mode."""
    clear_screen()
    schedule = schedules[index]
    total = len(schedules)
    
    # Check if schedule contains any subjects
    if not schedule.get("subjects"):
        console.print(
            "No sessions available for this schedule.",
            style="warning",
            justify="center",
        )
        console.print(
            "Use ←\→ arrows to navigate, q to quit",
            style="warning",
            justify="center",
        )
        return
    
    # Display subject details table
    header = Text("Schedule ", style="white") + Text(f"{index+1}/{total}", style="#FF5555")
    subject_table = Table(title=header, box=box.SIMPLE)
    subject_table.add_column("Subject", style="primary", header_style="bold")
    subject_table.add_column("Group", style="accent", header_style="bold")
    subject_table.add_column("Subgroup", style="accent", header_style="bold")
    
    for subject, info in schedule.get("subjects", {}).items():
        subject_table.add_row(subject, str(info.get("group", "")), str(info.get("subgroup", "")))
    
    # Create grid table
    grid = {}
    for subject, info in schedule.get("subjects", {}).items():
        for group_type in ("group", "subgroup"):
            group = info.get(group_type)
            if not group:
                continue
                
            for class_info in parsed_classes.get(subject, {}).get(str(group), []):
                key = (class_info["day"], class_info["hour"])
                grid.setdefault(key, []).append(subject)
    
    grid_table = Table(show_lines=True, title="Schedule", header_style="secondary", box=box.SIMPLE)
    grid_table.add_column("Hour/Day", style="primary", header_style="bold")
    
    for day in SHORT_WEEKDAYS:
        grid_table.add_column(day, style="accent", header_style="bold")
    
    for hour in range(start_hour, end_hour):
        row = [str(hour)]
        for day_index in range(len(SHORT_WEEKDAYS)):
            subjects = grid.get((day_index + 1, hour), [])
            row.append(", ".join(subjects))
        grid_table.add_row(*row)
    
    # Display tables
    console.print(grid_table, justify="center")
    console.print(subject_table, justify="center")
    
    # Show URL and navigation instructions
    console.print()
    console.print()
    console.print(
        Text(f"URL: {schedule['url']}", style="primary", no_wrap=True),
        justify="center",
    )
    console.print(
        "Use ←\→ arrows to navigate, q to quit", 
        style="warning", 
        justify="center"
    )


def display_splash_screen() -> None:
    """Display the application splash screen."""
    clear_screen()
    hide_cursor()
    
    # Generate title and center it
    splash = figlet_format("FIB Manager", font="chunky")
    subtitle = "Press any key to start"

    # Vertical centering
    height = console.height
    total_lines = splash.count("\n") + 1
    top_pad = max((height - total_lines) // 2, 0)
    
    for _ in range(top_pad):
        console.print()

    # Manual horizontal centering of each line
    width = console.width
    for line in splash.splitlines():
        pad = max((width - len(line)) // 2, 0)
        console.print(" " * pad + line, style="accent", markup=False)

    # Show subtitle
    console.print(subtitle, style="warning", justify="center")

    # Wait for key press
    msvcrt.getwch()


def select_year() -> int:
    """Prompt user to select a year."""
    current_year = date.today().year
    year_choices = [
        f"{current_year-1} (Last year)",
        f"{current_year} (Current year)",
        f"{current_year+1} (Next year)",
    ]
    
    selection = questionary.select(
        "Select Year:", choices=year_choices, style=QUESTIONARY_STYLE
    ).ask()
    
    return int(selection.split()[0])


def select_quadrimester_number() -> str:
    """Prompt user to select a quadrimester number."""
    return questionary.select(
        "Select Quadrimester:", choices=["1", "2"], style=QUESTIONARY_STYLE
    ).ask()


def select_language() -> str:
    """Prompt user to select a language."""
    lang_choice = questionary.select(
        "Select language:",
        choices=["English", "Spanish", "Catalan"],
        style=QUESTIONARY_STYLE,
    ).ask()
    
    return normalize_language(lang_choice)


def handle_subjects_command(args: Namespace) -> None:
    """Process the 'subjects' command to display available subjects."""
    lang = normalize_language(args.lang)
    raw_data = fetch_classes_data(args.quad, lang)
    parsed_data = parse_classes_data(raw_data)
    names = fetch_subject_names(lang)
    
    # Prepare subject data as a dictionary
    subjects_data = {
        subject: names.get(subject, subject) 
        for subject in sorted(parsed_data.keys())
    }
    
    if args.interface:
        # Display subjects in a styled table
        year, q_num = args.quad.split("Q")
        ordinal = "1st" if q_num == "1" else "2nd" if q_num == "2" else f"{q_num}th"
        table = Table(
            title=f"Subjects of the {ordinal} quarter of {year}",
            header_style="bright_red",
            box=box.SIMPLE,
        )
        
        table.add_column("Code", justify="right", style="bright_black", header_style="bold")
        table.add_column("Name", style="white", header_style="bold")
        
        for subject, name in subjects_data.items():
            table.add_row(subject, name)
            
        console.print(Align(table, align="center"))
    else:
        # Display subjects as plain JSON
        print(json.dumps(subjects_data, indent=2))


def display_subjects_list(quad: str, lang: str) -> None:
    """Display a list of subjects for interactive mode."""
    clear_screen()
    raw_data = fetch_classes_data(quad, lang)
    parsed_data = parse_classes_data(raw_data)
    names = fetch_subject_names(lang)
    
    # Display table with styling
    console.print()
    console.print()
    year, q_num = quad.split("Q")
    ordinal = "1st" if q_num == "1" else "2nd" if q_num == "2" else f"{q_num}th"
    table = Table(
        title=f"Subjects of the {ordinal} quarter of {year}",
        header_style="bright_red",
    )
    table.add_column("Code", justify="right", style="bright_black", header_style="bold")
    table.add_column("Name", style="white", header_style="bold")
    
    for subject in sorted(parsed_data.keys()):
        table.add_row(subject, names.get(subject, subject))
        
    console.print(Align(table, align="center"))
    
    # Display footer with exit instructions
    console.print()
    console.print(
        Align(Text("Q to quit\nESC to leave", style="accent", justify="center"), 
              align="center")
    )
    
    # Handle key presses
    while True:
        key = msvcrt.getwch()
        if key == "\x1b":  # ESC key
            show_cursor()
            clear_screen()
            break
        elif key.lower() == "q":
            show_cursor()
            sys.exit(0)


def get_groups_for_subjects(parsed_data: dict, subjects: list[str]) -> list[str]:
    """Extract group choices for the selected subjects only."""
    group_choices = []
    
    for subject in subjects:
        subject_data = parsed_data.get(subject, {})
        for group_id in subject_data:
            if group_id.isdigit():
                group_choices.append(f"{subject}-{group_id}")
    
    return sorted(group_choices)


def select_subject_search_params() -> tuple:
    """Prompt for and collect all schedule search parameters."""
    # Select quadrimester
    year = select_year()
    quad_num = select_quadrimester_number()
    quad = f"{year}Q{quad_num}"
    
    # Select languages
    languages_nat = questionary.checkbox(
        "Select languages:",
        choices=["English", "Spanish", "Catalan"],
        style=QUESTIONARY_STYLE,
        validate=lambda ans: True if ans else "Select at least one",
    ).ask()
    languages = [normalize_language(lang) for lang in languages_nat]
    lang_choice = languages[0]
    
    # Fetch and parse subjects data
    raw_data = fetch_classes_data(quad, "en")
    parsed_data = parse_classes_data(raw_data)
    names = fetch_subject_names("en")
    
    # Select subjects
    subject_choices = [
        f"{code} - {names.get(code, code)}"
        for code in sorted(parsed_data.keys())
    ]
    subjects_sel = questionary.checkbox(
        "Select subjects:",
        choices=subject_choices,
        style=QUESTIONARY_STYLE,
        validate=lambda ans: True if ans else "Select at least one",
    ).ask()
    subjects = [item.split(" - ", 1)[0].upper() for item in subjects_sel]
    
    # Select hours
    start_choices = [str(h) for h in range(8, 21)]
    start_hour = int(questionary.select(
        "Start hour:", choices=start_choices, style=QUESTIONARY_STYLE
    ).ask())
    
    end_choices = [str(h) for h in range(start_hour+1, 22)]
    end_hour = int(questionary.select(
        "End hour:", choices=end_choices, style=QUESTIONARY_STYLE
    ).ask())
    
    # Select blacklisted pairs - only show groups from selected subjects
    blacklist_choices = get_groups_for_subjects(parsed_data, subjects)
    blacklisted = questionary.checkbox(
        "Blacklisted pairs:", choices=blacklist_choices, style=QUESTIONARY_STYLE
    ).ask()
    
    # Select additional parameters
    same_subgroup = questionary.confirm(
        "Require same subgroup tens as group?", default=True, style=QUESTIONARY_STYLE
    ).ask()
    
    relax_choices = [str(i) for i in range(6)]
    relax_days = int(questionary.select(
        "Relaxable off-days:", choices=relax_choices, style=QUESTIONARY_STYLE
    ).ask())
    
    return (
        quad, subjects, start_hour, end_hour, 
        languages, lang_choice, blacklisted, same_subgroup, relax_days
    )


def handle_app_command(args: Namespace) -> None:
    """Process the 'app' command: enhanced interactive application."""
    if not check_windows_platform():
        return
        
    # Show splash screen
    display_splash_screen()
    
    # Main menu loop
    while True:
        clear_screen()
        choice = questionary.select(
            "Select option:",
            choices=["Search schedules", "List subjects", "Quit"],
            style=QUESTIONARY_STYLE,
        ).ask()
        
        clear_screen()
        
        if choice == "Quit" or choice is None:
            show_cursor()
            sys.exit(0)
            
        elif choice == "List subjects":
            # Get quadrimester selection
            year = select_year()
            quad_num = select_quadrimester_number()
            quad = f"{year}Q{quad_num}"
            
            # Get language selection
            lang_choice = select_language()
            
            # Display subjects
            display_subjects_list(quad, lang_choice)
            
        elif choice == "Search schedules":
            # Collect all search parameters
            (
                quad, subjects, start_hour, end_hour, 
                languages, lang_choice, blacklisted, same_subgroup, relax_days
            ) = select_subject_search_params()
            
            clear_screen()
            
            # Fetch and parse classes data
            raw_data = fetch_classes_data(quad, lang_choice)
            parsed_classes = parse_classes_data(raw_data)

            # Parse blacklist and search schedules
            parsed_blacklist = parse_blacklisted_pairs(blacklisted)
            result = get_schedule_combinations(
                quad,
                subjects,
                start_hour,
                end_hour,
                languages,
                same_subgroup,
                relax_days,
                parsed_blacklist,
                True,  # Always show progress bar in interactive app mode
            )
            schedules = result.get("schedules", [])

            if not schedules:
                console.print("No schedules found.", style="error", justify="center")
            else:
                navigate_schedules(schedules, parsed_classes, start_hour, end_hour)

# Add CLI entry point
def main() -> None:
    # try:
        default_quad = get_default_quadrimester()
        parser = setup_argument_parser(default_quad)
        args = parser.parse_args()

        if args.command == "search":
            handle_search_command(args)
        elif args.command == "subjects":
            handle_subjects_command(args)
        elif args.command == "app":
            handle_app_command(args)
        else:
            parser.print_help()
    # except:
    #     pass

if __name__ == "__main__":
    main()