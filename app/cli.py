import sys, os, json, logging, atexit, webbrowser
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
    ("qmark", "fg:#FF5555 bold"),
    ("question", "fg:#FFFFFF"),
    ("answer", "fg:#AAAAAA"),
    ("pointer", "fg:#666666 bold"),
    ("highlighted", "fg:#FF5555 bold"),
    ("selected", "fg:#AAAAAA"),
    ("separator", "fg:#AAAAAA"),
    ("instruction", "fg:#AAAAAA"),
    ("text", "fg:#AAAAAA"),
])

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
SUBJECT_COLORS = [
    "#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", 
    "#BAE1FF", "#FFECB3", "#D7BDE2", "#AED6F1",
]

console = Console(theme=UI_THEME)

def show_cursor() -> None:
    if sys.stdout.isatty():
        print("\033[?25h", end="", flush=True)

# Ensure terminal cursor gets restored
atexit.register(lambda: show_cursor() if sys.stdout.isatty() else None)

def hide_cursor() -> None:
    if sys.stdout.isatty():
        print("\033[?25l", end="", flush=True)

def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")

def get_default_quadrimester() -> str:
    today = date.today()
    half = 1 if today.month <= 6 else 2
    return f"{today.year-1}Q{half+1}"

def normalize_language(lang: str) -> str:
    return LANGUAGE_MAP.get(lang.lower(), lang)

def normalize_languages(langs: list[str]) -> list[str]:
    return [normalize_language(l) for l in langs]

def parse_blacklist(blacklist_items: list[str]) -> list[list[str, int]]:
    parsed = []
    for item in blacklist_items:
        if "-" not in item:
            continue
        subject, group = item.split("-", 1)
        if not group.isdigit():
            continue
        parsed.append([subject.upper(), int(group)])
    return parsed

def build_argument_parser(default_quad: str) -> ArgumentParser:
    parser = ArgumentParser(prog="fib-manager")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("app", help="start interactive application")
    
    schedules_parser = subparsers.add_parser("schedules", help="search schedule combinations")
    add_search_arguments(schedules_parser, default_quad)
    
    subjects_parser = subparsers.add_parser("subjects", help="show subjects for a quadrimester")
    add_subjects_arguments(subjects_parser, default_quad)
    
    return parser

def add_search_arguments(parser: ArgumentParser, default_quad: str) -> None:
    parser.add_argument("--debug", action="store_true", help="enable debug output")
    parser.add_argument("-q", "--quadrimester", default=default_quad, help=f"quadrimester code (e.g., {default_quad})")
    parser.add_argument("-s", "--subjects", nargs="+", required=True, help="list of subject codes")
    parser.add_argument("--start", type=int, default=8, help="start hour (inclusive)")
    parser.add_argument("--end", type=int, default=20, help="end hour (exclusive)")
    parser.add_argument("-l", "--languages", nargs="*", default=[], help="preferred class languages (e.g., en, es, ca)")
    parser.add_argument("--freedom", action="store_true", help="allow different subgroup than group")
    parser.add_argument("--days", type=int, default=5, help="maximum number of days with classes")
    parser.add_argument("--blacklist", nargs="*", default=[], help="blacklisted groups (e.g., IES-10)")
    parser.add_argument("-v", "--view", action="store_true", help="show search results in interactive interface")

def add_subjects_arguments(parser: ArgumentParser, default_quad: str) -> None:
    parser.add_argument("-q", "--quadrimester", default=default_quad, help=f"quadrimester code (e.g., {default_quad})")
    parser.add_argument("-l", "--language", default="en", help="language code for subject names (e.g., en, es, ca)")
    parser.add_argument("-v", "--view", action="store_true", help="display subjects in interactive interface")

def configure_debug_mode(enabled: bool) -> None:
    if not enabled:
        return
    logging.basicConfig(level=logging.DEBUG)
    import app.scheduler as sched
    sched.DEBUG = True

def print_json(data: dict) -> None:
    formatted = json.dumps(data, indent=2)
    if sys.stdout.isatty():
        print(formatted)
    else:
        sys.stdout.write(formatted)

# --- Schedule search and display functions ---
def perform_schedule_search(quad: str, subjects: list[str], start_hour: int, end_hour: int, 
                            languages: list[str], same_subgroup: bool, relax_days: int,
                            blacklisted: list[str], show_interface: bool=False) -> tuple:
    subjects = [s.upper() for s in subjects]
    blacklist_parsed = parse_blacklist(blacklisted)
    raw_data = fetch_classes_data(quad, "en")
    parsed_data = parse_classes_data(raw_data)
    search_result = get_schedule_combinations(
        quad, subjects, start_hour, end_hour, languages, same_subgroup, relax_days, 
        blacklist_parsed, show_interface
    )
    return search_result, parsed_data

def is_interactive_mode() -> bool:
    return sys.stdout.isatty() and msvcrt is not None

def check_windows_interactive() -> bool:
    if is_interactive_mode():
        return True
    console.print("Interactive mode requires a Windows terminal.", style="error", justify="center")
    show_cursor()
    return False

def create_schedule_grid(schedule: dict, parsed_classes: dict, start_hour: int, end_hour: int, subject_colors: dict) -> Table:
    grid = {}
    subjects_info = schedule.get("subjects", {})
    for subject, info in subjects_info.items():
        for grp_type in ("group", "subgroup"):
            group = info.get(grp_type)
            if not group:
                continue
            for class_info in parsed_classes.get(subject, {}).get(str(group), []):
                key = (class_info["day"], class_info["hour"])
                grid.setdefault(key, []).append((subject, class_info, info))
    table = Table(show_lines=True, title="Schedule", header_style="secondary", box=box.SIMPLE_HEAVY)
    table.add_column("Hour", justify="right", header_style="bold")
    for day in WEEKDAYS:
        table.add_column(day, justify="center", style="accent", header_style="bold")
    for hour in range(start_hour, end_hour):
        row = [str(hour)]
        for day_index in range(len(WEEKDAYS)):
            entries = grid.get((day_index + 1, hour), [])
            cell = Text()
            for subject, class_info, info in entries:
                type_letter = class_info.get("type", "")[:1].upper()
                flags = [LANG_FLAGS.get(normalize_language(lang.strip()), "") 
                         for lang in class_info.get("language", "").split(",") if lang.strip()]
                flag_text = " ".join(flags)
                group_val = info["group"] if class_info in parsed_classes.get(subject, {}).get(str(info["group"]), []) else info.get("subgroup", "")
                classroom = class_info.get("classroom", "").replace(",", "")
                line = f"{subject} {group_val}{type_letter}\n{classroom}\n{flag_text}"
                cell.append(line, style=subject_colors.get(subject, "primary"))
            row.append(cell)
        table.add_row(*row)
    return table

def create_subject_info_table(schedule: dict, subject_colors: dict) -> Table:
    table = Table(title="Subjects and Groups", header_style="secondary")
    table.add_column("Subject", justify="center", header_style="bold")
    table.add_column("Group", justify="center", header_style="bold")
    table.add_column("Subgroup", justify="center", header_style="bold")
    for subject, info in schedule.get("subjects", {}).items():
        style = subject_colors.get(subject, "primary")
        table.add_row(Text(subject, style=style), Text(str(info.get("group", "")), style=style),
                      Text(str(info.get("subgroup", "")), style=style))
    return table

def display_interface_schedule(index: int, total: int, schedules: list[dict], parsed_classes: dict,
                               start_hour: int, end_hour: int, subject_colors: dict, grid_view: bool) -> None:
    clear_screen()
    hide_cursor()
    schedule = schedules[index]
    if not schedule.get("subjects"):
        console.print("No sessions available for this schedule.", style="warning", justify="center")
        return
    header = Text("Schedule ", style="white") + Text(f"{index+1}", style="#FF5555") + \
             Text("/", style="bright_black") + Text(f"{total}", style="#FF5555")
    console.rule(header, style="accent")
    console.print("\n\n")
    if grid_view:
        grid_table = create_schedule_grid(schedule, parsed_classes, start_hour, end_hour, subject_colors)
        console.print(grid_table, justify="center")
    else:
        subj_table = create_subject_info_table(schedule, subject_colors)
        console.print(subj_table, justify="center")
    console.print("\n\n")
    console.print("SPACE to open schedule URL", style="primary", justify="center")
    toggle_text = "TAB to show groups" if grid_view else "TAB to show schedule"
    console.print(toggle_text, style="primary", justify="center")
    console.print("←→ to navigate", style="warning", justify="center")
    console.print("Q to quit\nESC to leave", style="accent", justify="center")

def navigate_schedules(schedules: list[dict], parsed_classes: dict, start_hour: int, end_hour: int) -> None:
    if not schedules:
        console.print("No schedules found.", style="error", justify="center")
        clear_screen()
        return
    total = len(schedules)
    current_index = 0
    grid_view = True
    subject_colors = {subject: SUBJECT_COLORS[i % len(SUBJECT_COLORS)] 
                      for i, subject in enumerate(sorted({s for sched in schedules for s in sched.get("subjects", {})}))}
    display_interface_schedule(current_index, total, schedules, parsed_classes, start_hour, end_hour, subject_colors, grid_view)
    while is_interactive_mode():
        key = msvcrt.getwch()
        if key == " ":
            webbrowser.open(schedules[current_index]["url"])
        elif key == "\t":
            grid_view = not grid_view
            display_interface_schedule(current_index, total, schedules, parsed_classes, start_hour, end_hour, subject_colors, grid_view)
        elif key == "\xe0":
            code = msvcrt.getwch()
            if code in ("M", "K"):
                current_index = (current_index + 1 if code == "M" else current_index - 1) % total
                display_interface_schedule(current_index, total, schedules, parsed_classes, start_hour, end_hour, subject_colors, grid_view)
        elif key.lower() == "q":
            show_cursor()
            sys.exit(0)
        elif key == "\x1b":
            break
    clear_screen()

# --- Splash Screen and user selection functions ---
def display_splash_screen() -> None:
    clear_screen()
    hide_cursor()
    splash = figlet_format("FIB   Manager", font="chunky")
    subtitle = "Press any key to start"
    top_pad = max((console.height - splash.count("\n") - 1) // 2, 0)
    print("\n" * top_pad, end="")
    for line in splash.splitlines():
        pad = max((console.width - len(line)) // 2, 0)
        console.print(" " * pad + line, style="accent", markup=False)
    console.print(subtitle, style="warning", justify="center")
    msvcrt.getwch()

def select_year() -> int:
    current_year = date.today().year
    choices = [str(current_year-1), str(current_year), str(current_year+1)]
    selection = questionary.select("Select Year:", choices=choices, instruction="(Use ↑↓ and Enter)", style=QUESTIONARY_STYLE).ask()
    return int(selection)

def select_quadrimester() -> str:
    return questionary.select("Select Quadrimester:", choices=["1", "2"], instruction="(Use ↑↓ and Enter)", style=QUESTIONARY_STYLE).ask()

def select_language() -> str:
    choice = questionary.select("Select language:", choices=["English", "Spanish", "Catalan"],
                                  instruction="(Use ↑↓ and Enter)", style=QUESTIONARY_STYLE,
                                  use_jk_keys=False, use_search_filter=True).ask()
    return normalize_language(choice)

def get_group_choices(parsed_data: dict, subjects: list[str]) -> list[str]:
    choices = []
    for subject in subjects:
        subj = subject.upper()
        for group in parsed_data.get(subj, {}):
            if group.isdigit():
                choices.append(f"{subj}-{group}")
    return sorted(choices)

def select_search_params() -> tuple:
    year = select_year()
    quad_num = select_quadrimester()
    quad = f"{year}Q{quad_num}"
    start_hour = int(questionary.select("Start hour:", choices=[str(h) for h in range(8, 21)],
                                        instruction="(Use ↑↓ and Enter)", style=QUESTIONARY_STYLE,
                                        use_jk_keys=False, use_search_filter=True).ask())
    end_hour = int(questionary.select("End hour:", choices=[str(h) for h in range(start_hour+1, 22)],
                                      instruction="(Use ↑↓ and Enter)", style=QUESTIONARY_STYLE,
                                      use_jk_keys=False, use_search_filter=True).ask())
    days = int(questionary.select("Maximum days with classes:", choices=[str(i) for i in range(1, 6)],
                                        default=5, instruction="(Use ↑↓ and Enter)", style=QUESTIONARY_STYLE,
                                        use_jk_keys=False, use_search_filter=True).ask())
    relax_days = 5 - days
    freedom = questionary.select("Allow different subgroup than group?",
                                 choices=["Yes", "No"], instruction="(Use ↑↓ and Enter)",
                                 style=QUESTIONARY_STYLE, use_jk_keys=False).ask() == "Yes"
    same_subgroup = not freedom
    languages_native = questionary.checkbox("Select languages of the classes:",
                                            choices=["English", "Spanish", "Catalan"],
                                            instruction="(Use ↑↓, Space toggle and Enter)",
                                            style=QUESTIONARY_STYLE, validate=lambda ans: True if ans else "Select at least one",
                                            use_jk_keys=False, use_search_filter=True).ask()
    languages = [normalize_language(l) for l in languages_native]
    raw_data = fetch_classes_data(quad, "en")
    parsed_data = parse_classes_data(raw_data)
    names = fetch_subject_names("en")
    subject_choices = [f"{code} - {names.get(code, code)}" for code in sorted(parsed_data.keys())]
    subjects_selected = questionary.checkbox("Select subjects:", choices=subject_choices,
                                               instruction="(Use ↑↓, Space toggle and Enter)",
                                               style=QUESTIONARY_STYLE, validate=lambda ans: True if ans else "Select at least one",
                                               use_jk_keys=False, use_search_filter=True).ask()
    subjects = [item.split(" - ", 1)[0].upper() for item in subjects_selected]
    blacklist_choices = get_group_choices(parsed_data, subjects)
    blacklisted = questionary.checkbox("Blacklisted groups:", choices=blacklist_choices,
                                       instruction="(Use ↑↓, Space toggle and Enter)", style=QUESTIONARY_STYLE,
                                       use_jk_keys=False, use_search_filter=True).ask()
    return quad, subjects, start_hour, end_hour, languages, blacklisted, same_subgroup, relax_days

def display_subjects_list(quad: str, lang: str) -> None:
    clear_screen()
    raw_data = fetch_classes_data(quad, lang)
    parsed_data = parse_classes_data(raw_data)
    names = fetch_subject_names(lang)
    year, quad_num = quad.split("Q")
    ordinal = "1st" if quad_num == "1" else "2nd" if quad_num == "2" else f"{quad_num}th"
    table = Table(title=f"Subjects of the {ordinal} quarter of {year}", header_style="bright_red")
    table.add_column("Code", justify="right", style="bright_black", header_style="bold")
    table.add_column("Name", style="white", header_style="bold")
    for subject in sorted(parsed_data.keys()):
        table.add_row(subject, names.get(subject, subject))
    console.print(Align(table, align="center"))
    console.print(Align(Text("Q to quit\nESC to leave", style="accent", justify="center"), align="center"))
    while True:
        key = msvcrt.getwch()
        if key == "\x1b":
            show_cursor()
            clear_screen()
            break
        elif key.lower() == "q":
            show_cursor()
            sys.exit(0)

def display_subjects_for_selection() -> None:
    year = select_year()
    quad_num = select_quadrimester()
    quad = f"{year}Q{quad_num}"
    lang_choice = select_language()
    display_subjects_list(quad, lang_choice)

# --- Command handlers ---
def handle_search_command(args: Namespace) -> None:
    configure_debug_mode(args.debug)
    args.languages = normalize_languages(args.languages)
    max_days = args.days
    relax_days = 5 - max_days
    freedom = args.freedom
    same_subgroup = not freedom
    result, classes = perform_schedule_search(args.quadrimester, args.subjects, args.start, args.end,
                                              args.languages, same_subgroup, relax_days,
                                              args.blacklist, args.view)
    if args.view:
        if not check_windows_interactive():
            return
        navigate_schedules(result.get("schedules", []), classes, args.start, args.end)
    else:
        print_json(result)

def handle_subjects_command(args: Namespace) -> None:
    lang = normalize_language(args.language)
    raw_data = fetch_classes_data(args.quadrimester, lang)
    parsed_data = parse_classes_data(raw_data)
    names = fetch_subject_names(lang)
    subjects_data = {subject: names.get(subject, subject) for subject in sorted(parsed_data.keys())}
    if args.view:
        year, quad_num = args.quadrimester.split("Q")
        ordinal = "1st" if quad_num=="1" else "2nd" if quad_num=="2" else f"{quad_num}th"
        table = Table(title=f"Subjects of the {ordinal} quarter of {year}", header_style="bright_red", box=box.SIMPLE)
        table.add_column("Code", justify="right", style="bright_black", header_style="bold")
        table.add_column("Name", style="white", header_style="bold")
        for subject, name in subjects_data.items():
            table.add_row(subject, name)
        console.print(Align(table, align="center"))
    else:
        print_json(subjects_data)

def handle_app_command(args: Namespace) -> None:
    if not check_windows_interactive():
        return
    display_splash_screen()
    while True:
        clear_screen()
        option = questionary.select("Select option:", choices=["Search schedules", "List subjects", "Quit"],
                                      instruction="(Use ↑↓ and Enter)", style=QUESTIONARY_STYLE,
                                      use_jk_keys=False, use_search_filter=True).ask()
        clear_screen()
        if option in ("Quit", None):
            show_cursor()
            sys.exit(0)
        elif option == "List subjects":
            display_subjects_for_selection()
        elif option == "Search schedules":
            perform_app_search()

def perform_app_search() -> None:
    quad, subjects, start_hour, end_hour, languages, blacklisted, same_subgroup, relax_days = select_search_params()
    clear_screen()
    result, parsed_data = perform_schedule_search(quad, subjects, start_hour, end_hour, languages,
                                                    same_subgroup, relax_days, blacklisted, True)
    schedules = result.get("schedules", [])
    if not schedules:
        console.print("No schedules found.", style="error", justify="center")
    else:
        navigate_schedules(schedules, parsed_data, start_hour, end_hour)

# --- CLI entry point ---
def main() -> None:
    default_quad = get_default_quadrimester()
    parser = build_argument_parser(default_quad)
    args = parser.parse_args()
    if args.command == "schedules":
        handle_search_command(args)
    elif args.command == "subjects":
        handle_subjects_command(args)
    elif args.command == "app":
        handle_app_command(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()