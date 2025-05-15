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
import atexit
from rich.align import Align

# Consolidated map for language normalization
LANGUAGE_MAP = {
    "catala": "ca",
    "català": "ca",
    "catalan": "ca",
    "ca": "ca",
    "castella": "es",
    "castellà": "es",
    "castellano": "es",
    "espanol": "es",
    "español": "es",
    "spanish": "es",
    "es": "es",
    "english": "en",
    "anglés": "en",
    "angles": "en",
    "inglés": "en",
    "ingles": "en",
    "en": "en",
}

# map language code to flag emoji
LANG_FLAGS = {"en": "ENG", "es": "ESP", "ca": "CAT"}

# Define a consistent color scheme (red, gray, white)
THEME = Theme(
    {
        "primary": "white",
        "secondary": "bright_black",
        "accent": "red",
        "warning": "bold red",
        "error": "bold red",
    }
)
console = Console(theme=THEME)

# Custom questionary style: using gray, light gray, white, light red via hex codes
Q_STYLE = QStyle(
    [
        ("qmark", "fg:#FF5555 bold"),  # light red
        ("question", "fg:#FFFFFF"),  # white
        ("answer", "fg:#AAAAAA"),  # light gray (changed)
        ("pointer", "fg:#666666 bold"),  # gray
        ("highlighted", "fg:#FF5555 bold"),  # light red
        ("selected", "fg:#AAAAAA"),  # light gray
        ("separator", "fg:#AAAAAA"),  # light gray
        ("instruction", "fg:#AAAAAA"),  # light gray
        ("text", "fg:#AAAAAA"),  # light gray (changed)
    ]
)

# ensure cursor is shown on program exit
atexit.register(lambda: print("\033[?25h", end="", flush=True))


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
    search.add_argument(
        "--quad", default=default_quad, help=f"Quadrimester code, e.g., {default_quad}"
    )
    search.add_argument(
        "--subjects", nargs="+", required=True, help="List of subject codes"
    )
    search.add_argument(
        "--start-hour", type=int, default=8, help="Start hour (inclusive)"
    )
    search.add_argument("--end-hour", type=int, default=20, help="End hour (exclusive)")
    search.add_argument(
        "--languages", nargs="*", default=[], help="Preferred class languages"
    )
    search.add_argument(
        "--same-subgroup-as-group",
        action="store_true",
        help="Require subgroup tens match group",
    )
    search.add_argument(
        "--relax-days", type=int, default=0, help="Number of relaxable off-days"
    )
    search.add_argument(
        "--blacklisted",
        nargs="*",
        default=[],
        help="Blacklisted subject-group pairs, e.g., IES-101",
    )
    search.add_argument(
        "--lang",
        default="en",
        help="Language code for subject names and API (e.g., en, es, ca)",
    )

    # Interface command
    interface = subparsers.add_parser("interface", help="Start interactive interface")
    interface.add_argument("--debug", action="store_true", help="Enable debug output")
    interface.add_argument(
        "--quad", default=default_quad, help=f"Quadrimester code, e.g., {default_quad}"
    )
    interface.add_argument(
        "--subjects", nargs="+", required=True, help="List of subject codes"
    )
    interface.add_argument(
        "--start-hour", type=int, default=8, help="Start hour (inclusive)"
    )
    interface.add_argument(
        "--end-hour", type=int, default=20, help="End hour (exclusive)"
    )
    interface.add_argument(
        "--languages", nargs="*", default=[], help="Preferred class languages"
    )
    interface.add_argument(
        "--same-subgroup-as-group",
        action="store_true",
        help="Require subgroup tens match group",
    )
    interface.add_argument(
        "--relax-days", type=int, default=0, help="Number of relaxable off-days"
    )
    interface.add_argument(
        "--blacklisted",
        nargs="*",
        default=[],
        help="Blacklisted subject-group pairs, e.g., IES-101",
    )
    interface.add_argument(
        "--lang",
        default="en",
        help="Language code for subject names and API (e.g., en, es, ca)",
    )

    # Subjects command
    subjects = subparsers.add_parser(
        "subjects", help="Show all available subjects for a quad"
    )
    subjects.add_argument(
        "-q",
        "--quad",
        default=default_quad,
        help=f"Quadrimester code, e.g., {default_quad}",
    )
    subjects.add_argument(
        "-l",
        "--lang",
        default="en",
        help="Language code for subject names (e.g., en, es, ca)",
    )

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
    # hide cursor when entering interface
    print("\033[?25l", end="", flush=True)
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        import app.scheduler as sched

        sched.DEBUG = True

    # Normalize languages and CLI lang same as search
    args.languages = [LANGUAGE_MAP.get(l.lower(), l) for l in args.languages]
    args.lang = LANGUAGE_MAP.get(args.lang.lower(), args.lang)
    blacklisted = parse_blacklisted(args.blacklisted)
    # Fetch and parse raw classes to build Schedule later
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
        # restore cursor before returning
        print("\033[?25h", end="", flush=True)
        return

    import os

    try:
        import msvcrt
    except ImportError:
        console.print(
            "Interactive mode is only supported on Windows.",
            style="error",
            justify="center",
        )
        # restore cursor before returning
        print("\033[?25h", end="", flush=True)
        return

    idx = 0

    def display(i: int) -> None:
        os.system("cls")
        sched_item = timetables[i]
        # Show message if no subjects in this schedule
        non_url = [k for k in sched_item.keys() if k != "url"]
        if not non_url:
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
        # Subject details table with styled header (white label + red count)
        header = Text("Schedule ", style="white") + Text(
            f"{i+1}/{total}", style="#FF5555"
        )
        subj_table = Table(title=header, box=box.SIMPLE)
        subj_table.add_column("Subject", style="primary", header_style="bold")
        subj_table.add_column("Group", style="accent", header_style="bold")
        subj_table.add_column("Subgroup", style="accent", header_style="bold")
        for subj, info in sched_item.items():
            if subj == "url":
                continue
            subj_table.add_row(subj, str(info["group"]), str(info["subgroup"]))
        # Grid table
        grid: dict[tuple[int, int], list[str]] = {}
        for subj, info in sched_item.items():
            if subj == "url":
                continue
            for grp in (info["group"], info["subgroup"]):
                for ci in parsed_classes.get(subj, {}).get(str(grp), []):
                    grid.setdefault((ci["day"], ci["hour"]), []).append(subj)
        grid_table = Table(
            show_lines=True, title="Schedule", header_style="secondary", box=box.SIMPLE
        )
        grid_table.add_column("Hour/Day", style="primary", header_style="bold")
        days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
        for d in days:
            grid_table.add_column(d, style="accent", header_style="bold")
        for h in range(args.start_hour, args.end_hour):
            row = [str(h)] + [
                ", ".join(grid.get((i + 1, h), [])) for i in range(len(days))
            ]
            grid_table.add_row(*row)
        console.print(grid_table, justify="center")
        console.print(subj_table, justify="center")
        console.print()
        console.print()
        console.print(
            Text(f"URL: {sched_item['url']}", style="primary", no_wrap=True),
            justify="center",
        )
        console.print(
            "Use ←\→ arrows to navigate, q to quit", style="warning", justify="center"
        )

    display(idx)
    while True:
        key = msvcrt.getwch()
        if key == "\xe0":  # special key prefix
            code = msvcrt.getwch()
            if code == "M":  # right arrow
                idx = (idx + 1) % total
                display(idx)
            elif code == "K":  # left arrow
                idx = (idx - 1) % total
                display(idx)
        elif key.lower() == "q":
            console.print("Exiting interface.", style="warning", justify="center")
            # restore cursor before leaving
            print("\033[?25h", end="", flush=True)
            break

    # clear screen and return (cursor already restored)
    os.system("cls")


def handle_app(args: Namespace) -> None:
    # Initial title screen
    os.system("cls")
    # hide cursor on splash/menu
    print("\033[?25l", end="", flush=True)
    # Generate FIGlet title and compute vertical and horizontal centering
    splash = figlet_format("FIB Horarios", font="chunky")
    subtitle = "Press any key to start"

    # Vertical centering
    height = console.height
    total_lines = splash.count("\n") + 1
    top_pad = max((height - total_lines) // 2, 0)
    for _ in range(top_pad):
        console.print()

    # Manual horizontal centering of each FIGlet line
    width = console.width
    for line in splash.splitlines():
        pad = max((width - len(line)) // 2, 0)
        console.print(" " * pad + line, style="accent", markup=False)

    # Subtitle (you can still use justify here)
    console.print(subtitle, style="warning", justify="center")

    # Wait for key press
    msvcrt.getwch()
    # Main menu loop
    while True:
        # Clear screen before showing main menu form
        os.system("cls")
        choice = questionary.select(
            "Select option:",
            choices=["Search schedules", "List subjects", "Quit"],
            style=Q_STYLE,
        ).ask()
        os.system("cls")
        if choice == "Quit" or choice is None:
            # restore cursor on exit
            print("\033[?25h", end="", flush=True)
            sys.exit(0)

        if choice == "List subjects":
            # Prompt quadrimester via two selectors
            # year selector
            year_choices = [
                f"{date.today().year-1} (Last year)",
                f"{date.today().year} (Current year)",
                f"{date.today().year+1} (Next year)",
            ]
            year = int(questionary.select(
                "Select Year:", choices=year_choices, style=Q_STYLE
            ).ask().split()[0])
            # quad number selector
            quad_num = questionary.select(
                "Select Quadrimester:", choices=["1", "2"], style=Q_STYLE
            ).ask()
            quad = f"{year}Q{quad_num}"
            # Ask for language before fetching subjects
            lang_choice = questionary.select(
                "Select language:",
                choices=["English", "Spanish", "Catalan"],
                style=Q_STYLE,
            ).ask()
            os.system("cls")
            lang_choice = LANGUAGE_MAP.get(lang_choice.lower(), lang_choice)
            raw = fetch_classes_data_with_language(quad, lang_choice)
            parsed = parse_classes_data(raw)
            names = fetch_subject_names(lang_choice)
            # Set subject list colors: light red header, light gray codes, white names
            console.print()
            console.print()
            table = Table(
                title=f"Subjects {quad}", header_style="bright_red"
            )
            # right-justify the code column
            table.add_column("Code", justify="right", style="bright_black", header_style="bold")
            table.add_column("Name", style="white", header_style="bold")
            for subj in sorted(parsed.keys()):
                table.add_row(subj, names.get(subj, subj))
            console.print(
                Align(table, align="center")
            )
            # Footer matches schedule searcher style/message
            console.print()
            console.print(
                Align(Text("Q to quit\nESC to leave", style="accent", justify="center"), align="center")
            )
            key = msvcrt.getwch()
            if key == "\x1b":  # ESC key
                # restore cursor if leaving subjects view
                print("\033[?25h", end="", flush=True)
                os.system("cls")
                continue
            elif key.lower() == "q":
                print("\033[?25h", end="", flush=True)
                sys.exit(0)

        elif choice == "Search schedules":
            # 1) Choose quad via two selectors
            year_choices = [
                f"{date.today().year-1} (Last year)",
                f"{date.today().year} (Current year)",
                f"{date.today().year+1} (Next year)",
            ]
            year = int(questionary.select(
                "Select Year:", choices=year_choices, style=Q_STYLE
            ).ask().split()[0])
            quad_num = questionary.select(
                "Select Quadrimester:", choices=["1", "2"], style=Q_STYLE
            ).ask()
            quad = f"{year}Q{quad_num}"

            # 2) Choose languages up-front
            languages_nat = questionary.checkbox(
                "Select languages:",
                choices=["English", "Spanish", "Catalan"],
                style=Q_STYLE,
                validate=lambda ans: True if ans and len(ans) > 0 else "Select at least one",
            ).ask()
            languages = [LANGUAGE_MAP.get(n.lower(), n) for n in languages_nat]
            lang_choice = languages[0]

            # 3) Fetch & parse to build subject list
            raw_sel = fetch_classes_data_with_language(quad, "en")
            parsed_sel = parse_classes_data(raw_sel)
            names = fetch_subject_names("en")

            # 4) Select subjects
            subject_choices = [
                f"{code} - {names.get(code, code)}"
                for code in sorted(parsed_sel.keys())
            ]
            subjects_sel = questionary.checkbox(
                "Select subjects:",
                choices=subject_choices,
                style=Q_STYLE,
                validate=lambda ans: True if ans and len(ans) > 0 else "Select at least one",
            ).ask()
            subjects = [item.split(" - ", 1)[0] for item in subjects_sel]

            # 5) hour selections: start 8–20, end start+1–21
            start_choices = [str(h) for h in range(8, 21)]
            start_hour = int(questionary.select(
                "Start hour:", choices=start_choices, style=Q_STYLE
            ).ask())
            end_choices = [str(h) for h in range(start_hour+1, 22)]
            end_hour = int(questionary.select(
                "End hour:", choices=end_choices, style=Q_STYLE
            ).ask())

            # 6) blacklisted subject-group pairs
            blacklist_choices = [
                f"{subj}-{grp}"
                for subj, groups in parsed_sel.items()
                for grp in groups.keys()
                if grp.isdigit()
            ]
            black = questionary.checkbox(
                "Blacklisted pairs:", choices=blacklist_choices, style=Q_STYLE
            ).ask()

            # 7) other params
            same = questionary.confirm(
                "Require same subgroup tens as group?", default=True, style=Q_STYLE
            ).ask()
            # free-days selector 0–5
            relax_choices = [str(i) for i in range(6)]
            relax = int(questionary.select(
                "Relaxable off-days:", choices=relax_choices, style=Q_STYLE
            ).ask())

            os.system("cls")

            # normalize blacklisted and run search
            blacklisted = parse_blacklisted(black)
            result = get_schedule_combinations(
                quad,
                subjects,
                start_hour,
                end_hour,
                languages,
                same,
                relax,
                blacklisted,
                lang_choice,
            )
            timetables = result.get("timetables", [])
            if not timetables:
                console.print("No schedules found.", style="error", justify="center")
                os.system("cls")
                continue
            raw_data = fetch_classes_data_with_language(quad, lang_choice)
            parsed_classes = parse_classes_data(raw_data)
            total = len(timetables)
            # Define pastel colors per subject
            all_subjects = sorted(
                {s for sched in timetables for s in sched if s != "url"}
            )
            colors = [
                "#FFB3BA",
                "#FFDFBA",
                "#FFFFBA",
                "#BAFFC9",
                "#BAE1FF",
                "#FFECB3",
                "#D7BDE2",
                "#AED6F1",
            ]
            subject_colors = {
                subj: colors[i % len(colors)] for i, subj in enumerate(all_subjects)
            }
            idx = 0
            # toggle state: True for grid view, False for group table view
            show_grid = [True]

            # Navigate schedules
            def render(i: int) -> None:
                os.system("cls")
                sched_item = timetables[i]
                non_url = [k for k in sched_item.keys() if k != "url"]
                if not non_url:
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
                # Colored schedule header: white label, red count
                header = (
                    Text("Schedule ", style="white")
                    + Text(str(i + 1), style="#FF5555")
                    + Text("/", style="bright_black")
                    + Text(str(total), style="#FF5555")
                )
                console.rule(header, style="accent")
                # Subject details
                subj_table = Table(
                    title="Subjects and groups", header_style="secondary"
                )
                subj_table.add_column("Subject", justify="center", header_style="bold")
                subj_table.add_column("Group", justify="center", header_style="bold")
                subj_table.add_column("Subgroup", justify="center", header_style="bold")
                sched_item = timetables[i]
                for subj, info in sched_item.items():
                    if subj == "url":
                        continue
                    subj_table.add_row(
                        Text(subj, style=subject_colors.get(subj, "primary")),
                        Text(
                            str(info["group"]),
                            style=subject_colors.get(subj, "primary"),
                        ),
                        Text(
                            str(info["subgroup"]),
                            style=subject_colors.get(subj, "primary"),
                        ),
                    )
                # Schedule
                days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
                hours = list(range(start_hour, end_hour))
                grid = {}
                for subj, info in sched_item.items():
                    if subj == "url":
                        continue
                    for grp in (info["group"], info["subgroup"]):
                        for ci in parsed_classes.get(subj, {}).get(str(grp), []):
                            grid.setdefault((ci["day"], ci["hour"]), []).append(
                                (subj, ci, info)
                            )
                grid_table = Table(
                    show_lines=True,
                    title="Schedule",
                    box=box.SIMPLE_HEAVY,
                    header_style="secondary",
                )
                grid_table.add_column(justify="right", header_style="bold")
                for d in days:
                    grid_table.add_column(
                        d, style="accent", header_style="bold", justify="center"
                    )
                for h in hours:
                    # Build styled cell per day
                    row = [str(h)]
                    for di in range(len(days)):
                        entries = grid.get((di + 1, h), [])
                        cell = Text()
                        for subj, ci, info in entries:
                            # show SUBJECT, first letter of type, and flag emoji
                            t = ci.get("type", "")
                            letter = t[0].upper() if t else ""
                            flag = ""
                            for lang in ci.get("language", "").split(","):
                                flag += " " + LANG_FLAGS.get(
                                    LANGUAGE_MAP.get(lang.lower(), "en"), ""
                                )
                            flag = flag.strip()
                            group = info["group"] if letter == "T" else info["subgroup"]
                            line1 = f"{subj} {group}{letter}"
                            line2 = f"{ci.get('classroom', '')}".replace(",", "")
                            line3 = f"{flag}"
                            line = f"{line1}\n{line2}\n{line3}"
                            cell.append(line, style=subject_colors.get(subj, "primary"))
                        row.append(cell)
                    grid_table.add_row(*row)
                # only one view at a time
                console.print()
                console.print()
                if show_grid[0]:
                    console.print(grid_table, justify="center")
                else:
                    console.print(subj_table, justify="center")

                console.print()
                console.print()
                console.print(
                    "Press SPACE to open schedule URL",
                    style="primary",
                    justify="center",
                )
                console.print(
                    "Press TAB to show groups" if show_grid[0] else "Press TAB to show schedule",
                    style="primary",
                    justify="center",
                )
                console.print()
                console.print("←→ to navigate", style="warning", justify="center")
                console.print()
                console.print(
                    "Q to quit\nESC to leave", style="accent", justify="center"
                )

            render(idx)
            while True:
                key = msvcrt.getwch()
                if key == " ":
                    # Open the current schedule URL
                    webbrowser.open(timetables[idx]["url"])
                elif key == "\t":
                    # toggle between grid and group views
                    show_grid[0] = not show_grid[0]
                    render(idx)
                elif key == "\xe0":  # arrow keys
                    code = msvcrt.getwch()
                    if code == "M":  # right arrow
                        idx = (idx + 1) % total
                        render(idx)
                    elif code == "K":  # left arrow
                        idx = (idx - 1) % total
                        render(idx)
                elif key.lower() == "q":
                    print("\033[?25h", end="", flush=True)
                    sys.exit(0)
                elif key == "\x1b":  # ESC
                    break
            os.system("cls")
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
    table = Table(
        title=f"Subjects {args.quad} ({lang})",
        header_style="bright_red",
        box=box.SIMPLE,
    )
    # right-justify the code column
    table.add_column("Code", justify="right", style="bright_black", header_style="bold")
    table.add_column("Name", style="white", header_style="bold")
    for subj in sorted(parsed.keys()):
        table.add_row(subj, names.get(subj, subj))
    console.print(
        Align(table, align="center")
    )


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
