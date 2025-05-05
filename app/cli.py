import json
import logging
from datetime import date
from argparse import ArgumentParser, Namespace
from app.scheduler import (
    get_schedule_combinations,
    fetch_classes_data_with_language,
    parse_classes_data,
    fetch_subject_names,
)
from rich.console import Console
from rich.table import Table
import questionary
from pyfiglet import figlet_format
from rich import box
import os
import msvcrt
from rich.theme import Theme
from rich.text import Text
from questionary import Style as QStyle
import sys
import webbrowser

# Consolidated map for language normalization
LANGUAGE_MAP = {
    "catala": "ca", "català": "ca", "catalan": "ca", "ca": "ca",
    "castella": "es", "castellà": "es", "castellano": "es", "espanol": "es", "español": "es", "spanish": "es", "es": "es",
    "english": "en", "anglés": "en", "angles": "en", "inglés": "en", "ingles": "en", "en": "en",
}

# Define a consistent color scheme (red, gray, white)
THEME = Theme({
    "primary": "white",
    "secondary": "bright_black",
    "accent": "red",
    "warning": "bold red",
    "error": "bold red",
})
console = Console(theme=THEME)

# Custom questionary style: using gray, light gray, white, light red via hex codes
Q_STYLE = QStyle([
    ('qmark', 'fg:#FF5555 bold'),      # light red
    ('question', 'fg:#FFFFFF'),        # white
    ('answer', 'fg:#FFFFFF'),          # white
    ('pointer', 'fg:#666666 bold'),    # gray
    ('highlighted', 'fg:#FF5555 bold'),# light red
    ('selected', 'fg:#AAAAAA'),        # light gray
    ('separator', 'fg:#AAAAAA'),       # light gray
    ('instruction', 'fg:#AAAAAA'),     # light gray
    ('text', 'fg:#FFFFFF'),            # white
])


def get_default_quad() -> str:
    """Compute default quadrimester based on current date."""
    today = date.today()
    half = 1 if today.month <= 6 else 2
    return f"{today.year-1}Q{half+1}"


def parse_blacklisted(items: list[str]) -> list[tuple[str, int]]:
    """Parse blacklisted subject-group strings into tuples."""
    parsed: list[tuple[str, int]] = []
    for item in items:
        if "-" in item:
            subj, grp = item.split("-", 1)
            if grp.isdigit():
                parsed.append((subj, int(grp)))
    return parsed


def configure_parser(default_quad: str) -> ArgumentParser:
    """Set up the argument parser with subcommands and options."""
    parser = ArgumentParser(prog="fib-horarios")
    subparsers = parser.add_subparsers(dest="command")
    # Enhanced interactive app command
    subparsers.add_parser("app", help="Start enhanced interactive application")
     
    # Search command
    search = subparsers.add_parser("search", help="Search for schedule combinations")
    search.add_argument("--debug", action="store_true", help="Enable debug output")
    search.add_argument("--quad", default=default_quad, help=f"Quadrimester code, e.g., {default_quad}")
    search.add_argument("--subjects", nargs="+", required=True, help="List of subject codes")
    search.add_argument("--start-hour", type=int, default=8, help="Start hour (inclusive)")
    search.add_argument("--end-hour", type=int, default=20, help="End hour (exclusive)")
    search.add_argument("--languages", nargs="*", default=[], help="Preferred class languages")
    search.add_argument("--same-subgroup-as-group", action="store_true",
                         help="Require subgroup tens match group")
    search.add_argument("--relax-days", type=int, default=0, help="Number of relaxable off-days")
    search.add_argument("--blacklisted", nargs="*", default=[], help="Blacklisted subject-group pairs, e.g., IES-101")
    search.add_argument("--lang", default="en", help="Language code for subject names and API (e.g., en, es, ca)")

    # Interface command
    interface = subparsers.add_parser("interface", help="Start interactive interface")
    interface.add_argument("--debug", action="store_true", help="Enable debug output")
    interface.add_argument("--quad", default=default_quad, help=f"Quadrimester code, e.g., {default_quad}")
    interface.add_argument("--subjects", nargs="+", required=True, help="List of subject codes")
    interface.add_argument("--start-hour", type=int, default=8, help="Start hour (inclusive)")
    interface.add_argument("--end-hour", type=int, default=20, help="End hour (exclusive)")
    interface.add_argument("--languages", nargs="*", default=[], help="Preferred class languages")
    interface.add_argument("--same-subgroup-as-group", action="store_true",
                          help="Require subgroup tens match group")
    interface.add_argument("--relax-days", type=int, default=0, help="Number of relaxable off-days")
    interface.add_argument("--blacklisted", nargs="*", default=[], help="Blacklisted subject-group pairs, e.g., IES-101")
    interface.add_argument("--lang", default="en", help="Language code for subject names and API (e.g., en, es, ca)")

    # Subjects command
    subjects = subparsers.add_parser("subjects", help="Show all available subjects for a quad")
    subjects.add_argument("-q", "--quad", default=default_quad,
                           help=f"Quadrimester code, e.g., {default_quad}")
    subjects.add_argument("-l", "--lang", default="en",
                           help="Language code for subject names (e.g., en, es, ca)")

    return parser


def handle_search(args: Namespace) -> None:
    """Process the 'search' command."""
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        import app.scheduler as sched
        sched.DEBUG = True

    # Normalize languages and CLI lang
    args.languages = [LANGUAGE_MAP.get(l.lower(), l) for l in args.languages]
    args.lang = LANGUAGE_MAP.get(args.lang.lower(), args.lang)

    blacklisted = parse_blacklisted(args.blacklisted)
    result = get_schedule_combinations(
        args.quad,
        args.subjects,
        args.start_hour,
        args.end_hour,
        args.languages,
        args.same_subgroup_as_group,
        args.relax_days,
        blacklisted,
        args.lang,
    )
    console.rule(" Search Results ", style="secondary")
    console.print_json(data=result)
    console.rule(style="secondary")


def handle_interface(args: Namespace) -> None:
    """Process the 'interface' command: interactive schedule navigation."""
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        import app.scheduler as sched
        sched.DEBUG = True

    # Normalize languages and CLI lang same as search
    args.languages = [LANGUAGE_MAP.get(l.lower(), l) for l in args.languages]
    args.lang = LANGUAGE_MAP.get(args.lang.lower(), args.lang)
    blacklisted = parse_blacklisted(args.blacklisted)
    # Fetch and parse raw classes to build schedule grid later
    raw_classes = fetch_classes_data_with_language(args.quad, args.lang)
    parsed_classes = parse_classes_data(raw_classes)
    result = get_schedule_combinations(
        args.quad,
        args.subjects,
        args.start_hour,
        args.end_hour,
        args.languages,
        args.same_subgroup_as_group,
        args.relax_days,
        blacklisted,
        args.lang,
    )
    timetables = result.get("timetables", [])
    total = len(timetables)
    if total == 0:
        console.print("No schedules found to display.", style="error", justify="center")
        return

    import os
    try:
        import msvcrt
    except ImportError:
        console.print("Interactive mode is only supported on Windows.", style="error", justify="center")
        return

    idx = 0
    def display(i: int) -> None:
        os.system('cls')
        sched_item = timetables[i]
        # Show message if no subjects in this schedule
        non_url = [k for k in sched_item.keys() if k != 'url']
        if not non_url:
            console.print("No sessions available for this schedule.", style="warning", justify="center")
            console.print("Use ←/→ arrows to navigate, q to quit", style="warning", justify="center")
            return
        # Subject details table with styled header (white label + red count)
        header = Text("Schedule ", style="white") + Text(f"{i+1}/{total}", style="#FF5555")
        subj_table = Table(title=header, box=box.SIMPLE)
        subj_table.add_column("Subject", style="primary")
        subj_table.add_column("Group", style="accent")
        subj_table.add_column("Subgroup", style="accent")
        for subj, info in sched_item.items():
            if subj == 'url': continue
            subj_table.add_row(subj, str(info['group']), str(info['subgroup']))
        # Grid table
        grid: dict[tuple[int,int], list[str]] = {}
        for subj, info in sched_item.items():
            if subj == 'url': continue
            for grp in (info['group'], info['subgroup']):
                for ci in parsed_classes.get(subj, {}).get(str(grp), []):
                    grid.setdefault((ci['day'], ci['hour']), []).append(subj)
        grid_table = Table(show_lines=True, title="Schedule Grid", header_style="secondary", box=box.SIMPLE)
        grid_table.add_column("Hour/Day", style="primary")
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
        for d in days:
            grid_table.add_column(d, style="accent")
        for h in range(args.start_hour, args.end_hour):
            row = [str(h)] + [", ".join(grid.get((i+1, h), [])) for i in range(len(days))]
            grid_table.add_row(*row)
        console.print(grid_table, justify="center")
        console.print(subj_table, justify="center")
        console.print()
        console.print()
        console.print(Text(f"URL: {sched_item['url']}", style="primary", no_wrap=True), justify="center")
        console.print("Use ←/→ arrows to navigate, q to quit", style="warning", justify="center")

    display(idx)
    while True:
        key = msvcrt.getwch()
        if key == '\xe0':  # special key prefix
            code = msvcrt.getwch()
            if code == 'M':  # right arrow
                idx = (idx + 1) % total
                display(idx)
            elif code == 'K':  # left arrow
                idx = (idx - 1) % total
                display(idx)
        elif key.lower() == 'q':
            console.print("Exiting interface.", style="warning", justify="center")
            break


def handle_app(args: Namespace) -> None:
    # Initial title screen
    os.system('cls')
    console.rule(style="secondary")
    # Generate FIGlet title and pad all lines to equal length
    title = figlet_format("FIB Horarios", font="chunky")
    width = console.width
    lines = title.splitlines()[:-1]  # skip the last line
    for line in lines:
        pad = max((width - len(line)) // 2, 0)
        console.print(" " * pad + line, style="accent", markup=False)
    console.rule(style="secondary")
    console.print("Press any key to start", style="warning", justify="center")
    msvcrt.getwch()
    os.system('cls')
    # Main menu loop
    while True:
        # Clear screen before showing main menu form
        os.system('cls')
        choice = questionary.select(
            "Select option:", choices=["Search schedules", "List subjects", "Quit"], style=Q_STYLE
        ).ask()
        os.system('cls')
        if choice == "Quit" or choice is None:
            sys.exit(0)

        if choice == "List subjects":
            # List subjects and await user input to exit or return
            # Prompt quadrimester code with custom style and clear screen after input
            quad = questionary.text("Quadrimester code:", default=get_default_quad(), style=Q_STYLE).ask()
            # Prompt language code with custom style
            lang_choice = questionary.select(
                "Language code:", choices=["en", "es", "ca"], default="en", style=Q_STYLE
            ).ask()
            os.system('cls')
            lang_choice = LANGUAGE_MAP.get(lang_choice.lower(), lang_choice)
            raw = fetch_classes_data_with_language(quad, lang_choice)
            parsed = parse_classes_data(raw)
            names = fetch_subject_names(lang_choice)
            # Set subject list colors: light red header, light gray codes, white names
            table = Table(title=f"Subjects {quad} ({lang_choice})", header_style="bright_red")
            table.add_column("Code", style="bright_black")
            table.add_column("Name", style="white")
            for subj in sorted(parsed.keys()):
                table.add_row(subj, names.get(subj, subj))
            console.print(table, justify="center")
            # Prompt for exit or back
            # Improved navigation prompt, clear screen on go-back
            console.print("Press Esc to go back or 'q' to quit", style="bright_red", justify="center")
            key = msvcrt.getwch()
            if key == '\x1b':  # ESC key
                os.system('cls')
                continue
            elif key.lower() == 'q':
                sys.exit(0)

        elif choice == "Search schedules":
            # Collect parameters with custom style
            quad = questionary.text("Quadrimester code:", default=get_default_quad(), style=Q_STYLE).ask()
            # Subjects input, convert to uppercase codes
            subjects = questionary.text("Subjects (space-separated):", style=Q_STYLE).ask().split()
            subjects = [s.upper() for s in subjects]
            start_hour = int(questionary.text("Start hour:", default="8", style=Q_STYLE).ask())
            end_hour = int(questionary.text("End hour:", default="20", style=Q_STYLE).ask())
            # Languages selection list (natural names), must choose at least one
            languages_nat = questionary.checkbox(
                "Select languages:", choices=["English", "Spanish", "Catalan"], style=Q_STYLE,
                validate=lambda ans: True if ans and len(ans) > 0 else "Select at least one"
            ).ask()
            # Additional schedule parameters
            same = questionary.confirm("Require same subgroup tens as group?", default=True, style=Q_STYLE).ask()
            relax = int(questionary.text("Relaxable off-days:", default="0", style=Q_STYLE).ask())
            black = questionary.text("Blacklisted pairs (space-separated):", default="", style=Q_STYLE).ask().split()
            # Clear screen before showing results or proceeding
            os.system('cls')
            # Map natural language names to codes, derive primary lang
            languages = [LANGUAGE_MAP.get(n.lower(), n) for n in languages_nat]
            lang_choice = languages[0]
            # Normalize inputs
            blacklisted = parse_blacklisted(black)
            # Fetch timetables
            result = get_schedule_combinations(
                quad, subjects, start_hour, end_hour,
                languages, same, relax, blacklisted, lang_choice
            )
            timetables = result.get("timetables", [])
            if not timetables:
                console.print("No schedules found.", style="error", justify="center")
                os.system('cls')
                continue
            raw_data = fetch_classes_data_with_language(quad, lang_choice)
            parsed_classes = parse_classes_data(raw_data)
            total = len(timetables)
            # Define pastel colors per subject
            all_subjects = sorted({s for sched in timetables for s in sched if s != 'url'})
            colors = ["#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF", "#FFECB3", "#D7BDE2", "#AED6F1"]
            subject_colors = {subj: colors[i % len(colors)] for i, subj in enumerate(all_subjects)}
            idx = 0
            # Navigate schedules
            def render(i: int) -> None:
                os.system('cls')
                sched_item = timetables[i]
                non_url = [k for k in sched_item.keys() if k != 'url']
                if not non_url:
                    console.print("No sessions available for this schedule.", style="warning", justify="center")
                    console.print("Use ←/→ to navigate, q to quit", style="warning", justify="center")
                    return
                # Colored schedule header: white label, red count
                header = (
                    Text("Schedule ", style="white")
                    + Text(str(i+1), style="#FF5555")
                    + Text("/", style="bright_black")
                    + Text(str(total), style="#FF5555")
                )
                console.rule(header, style="accent")
                # Subject details
                subj_table = Table(title="Subjects", header_style="secondary")
                subj_table.add_column("Subject")
                subj_table.add_column("Group")
                subj_table.add_column("Subgroup")
                sched_item = timetables[i]
                for subj, info in sched_item.items():
                    if subj == 'url': continue
                    subj_table.add_row(
                        Text(subj, style=subject_colors.get(subj, 'primary')), 
                        Text(str(info['group']), style=subject_colors.get(subj, 'primary')),
                        Text(str(info['subgroup']), style=subject_colors.get(subj, 'primary'))
                    )
                # Schedule grid
                days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
                hours = list(range(start_hour, end_hour))
                grid = {}
                for subj, info in sched_item.items():
                    if subj == 'url': continue
                    for grp in (info['group'], info['subgroup']):
                        for ci in parsed_classes.get(subj, {}).get(str(grp), []):
                            grid.setdefault((ci['day'], ci['hour']), []).append(subj)
                grid_table = Table(show_lines=True, title="Schedule Grid", box=box.SIMPLE_HEAVY, header_style="secondary")
                grid_table.add_column(justify="right")
                for d in days:
                    grid_table.add_column(d, style="accent")
                for h in hours:
                    # Build styled cell per day
                    row = [str(h)]
                    for di in range(len(days)):
                        subs = grid.get((di+1, h), [])
                        cell = Text()
                        for sub in subs:
                            cell.append(sub, style=subject_colors.get(sub, 'primary'))
                            cell.append(" ")
                        row.append(cell)
                    grid_table.add_row(*row)
                console.print()
                console.print()
                console.print(grid_table, justify="center")
                console.print()
                console.print()  # spacing between grid and subjects
                console.print(subj_table, justify="center")
                console.print()
                console.print()
                console.print(Text(f"URL\n{sched_item['url']}", style="primary", no_wrap=True), justify="center")
                console.print()
                console.print()
                console.print("←/→ to navigate, Q to quit", style="warning", justify="center")
                console.print("Press any key to open schedule URL in browser", style="accent", justify="center")
                msvcrt.getwch()
                webbrowser.open(sched_item['url'])

            # Navigation loop
            render(idx)
            while True:
                key = msvcrt.getwch()
                if key == '\xe0':
                    code = msvcrt.getwch()
                    if code == 'M':
                        idx = (idx + 1) % total
                        render(idx)
                    elif code == 'K':
                        idx = (idx - 1) % total
                        render(idx)
                elif key.lower() == 'q':
                    break
            os.system('cls')
            continue
        else:
            continue


def handle_subjects(args: Namespace) -> None:
    """Process the 'subjects' command."""
    lang = LANGUAGE_MAP.get(args.lang.lower(), args.lang)
    raw = fetch_classes_data_with_language(args.quad, lang)
    parsed = parse_classes_data(raw)
    names = fetch_subject_names(lang)
    # Display subjects in a styled table
    # Use only gray, light gray, white, and light red for subject list
    table = Table(title=f"Subjects {args.quad} ({lang})", header_style="bright_red", box=box.SIMPLE)
    table.add_column("Code", style="bright_black")
    table.add_column("Name", style="white")
    for subj in sorted(parsed.keys()):
        table.add_row(subj, names.get(subj, subj))
    console.print(table, justify="center")


def main() -> None:
    """Entry point for CLI."""
    default_quad = get_default_quad()
    parser = configure_parser(default_quad)
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "search":
        handle_search(args)
    elif args.command == "interface":
        handle_interface(args)
    elif args.command == "app":
        handle_app(args)
    else:
        handle_subjects(args)


if __name__ == "__main__":
    main()
