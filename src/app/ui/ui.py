"""
User interface module for FIB Manager.
"""

import sys
import webbrowser
import atexit
import msvcrt
from typing import Dict, List, Any
from pyfiglet import figlet_format
from rich.console import Console
from rich.table import Table
from rich.theme import Theme
from rich.text import Text
from rich.align import Align
from rich import box
import questionary
from questionary import Style as QStyle

from app.core.constants import WEEKDAYS, LANG_FLAGS, SUBJECT_COLORS, SORT_MODE_GROUPS, SORT_MODE_DEAD_HOURS
from app.core.utils import clear_screen, hide_cursor, show_cursor, normalize_language, is_interactive_mode
from app.core.parser import parse_classes_data
from app.core.validator import sort_schedules_by_mode

# Setup console and theme
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

console = Console(theme=UI_THEME)

# Ensure terminal cursor gets restored
atexit.register(lambda: show_cursor() if sys.stdout.isatty() else None)


def check_windows_interactive() -> bool:
    """
    Check if we're in an interactive Windows terminal.
    
    Returns:
        True if we're in an interactive Windows terminal, False otherwise
    """
    if is_interactive_mode():
        return True
    console.print("Interactive mode requires a Windows terminal.", style="error", justify="center")
    show_cursor()
    return False


def create_schedule_grid(schedule: dict, parsed_classes: dict, start_hour: int, end_hour: int, subject_colors: dict) -> Table:
    """
    Create a grid table for displaying a schedule.
    
    Args:
        schedule: Schedule dictionary
        parsed_classes: Parsed class data
        start_hour: Minimum hour to display
        end_hour: Maximum hour to display
        subject_colors: Dictionary mapping subjects to colors
    
    Returns:
        Rich Table object
    """
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
        row = [f"{hour} - {hour + 1}"]
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
    """
    Create a table for displaying subject information.
    
    Args:
        schedule: Schedule dictionary
        subject_colors: Dictionary mapping subjects to colors
    
    Returns:
        Rich Table object
    """
    table = Table(title="Subjects and Groups", header_style="secondary")
    table.add_column("Subject", justify="center", header_style="bold")
    table.add_column("Group", justify="center", header_style="bold")
    table.add_column("Subgroup", justify="center", header_style="bold")
    
    for subject, info in schedule.get("subjects", {}).items():
        style = subject_colors.get(subject, "primary")
        table.add_row(
            Text(subject, style=style), 
            Text(str(info.get("group", "")), style=style),
            Text(str(info.get("subgroup", "")), style=style)
        )
    
    return table


def display_interface_schedule(index: int, total: int, schedules: list[dict], parsed_classes: dict,
                               start_hour: int, end_hour: int, subject_colors: dict, grid_view: bool) -> None:
    """
    Display a schedule in the interface.
    
    Args:
        index: Index of the schedule to display
        total: Total number of schedules
        schedules: List of schedules
        parsed_classes: Parsed class data
        start_hour: Minimum hour to display
        end_hour: Maximum hour to display
        subject_colors: Dictionary mapping subjects to colors
        grid_view: Whether to display the schedule as a grid
    """
    clear_screen()
    hide_cursor()
    schedule = schedules[index]
    
    if not schedule.get("subjects"):
        console.print("No sessions available for this schedule.", style="warning", justify="center")
        return
    
    header = Text("Schedule ", style="white") + Text(f"{index+1}", style="#FF5555") + \
             Text("/", style="bright_black") + Text(f"{total}", style="#FF5555")
    console.rule(header, style="accent")
    console.print()
    
    if grid_view:
        grid_table = create_schedule_grid(schedule, parsed_classes, start_hour, end_hour, subject_colors)
        console.print(grid_table, justify="center")
    else:
        subj_table = create_subject_info_table(schedule, subject_colors)
        console.print(subj_table, justify="center")
        console.print()
    
    console.print("SPACE to open schedule URL", style="primary", justify="center")
    toggle_text = "TAB to show groups" if grid_view else "TAB to show schedule"
    console.print(toggle_text, style="primary", justify="center")
    console.print("←→ to navigate", style="warning", justify="center")
    console.print("ESC to leave\nQ to quit", style="accent", justify="center")


def display_interface_schedule_with_sort(index: int, total: int, schedules: list[dict], parsed_classes: dict,
                                         start_hour: int, end_hour: int, subject_colors: dict, grid_view: bool, 
                                         sort_mode: str) -> None:
    """
    Display a schedule in the interface with sorting information.
    
    Args:
        index: Index of the schedule to display
        total: Total number of schedules
        schedules: List of schedules
        parsed_classes: Parsed class data
        start_hour: Minimum hour to display
        end_hour: Maximum hour to display
        subject_colors: Dictionary mapping subjects to colors
        grid_view: Whether to display the schedule as a grid
        sort_mode: Current sorting mode
    """
    clear_screen()
    hide_cursor()
    schedule = schedules[index]
    
    if not schedule.get("subjects"):
        console.print("No sessions available for this schedule.", style="warning", justify="center")
        return    # Create simple header
    header = Text("Schedule ", style="white") + Text(f"{index+1}", style="#FF5555") + \
             Text("/", style="bright_black") + Text(f"{total}", style="#FF5555")
    
    console.rule(header, style="accent")
    console.print()
    
    if grid_view:
        grid_table = create_schedule_grid(schedule, parsed_classes, start_hour, end_hour, subject_colors)
        console.print(grid_table, justify="center")
    else:
        subj_table = create_subject_info_table(schedule, subject_colors)
        console.print(subj_table, justify="center")
        console.print()
    console.print("SPACE to open schedule URL", style="primary", justify="center")
    toggle_text = "TAB to show groups" if grid_view else "TAB to show schedule"
    console.print(toggle_text, style="primary", justify="center")
    
    # Add sort toggle information (showing the opposite mode that will be activated)
    if sort_mode == SORT_MODE_GROUPS:
        sort_text = "S to sort by dead hours"
    else:  # SORT_MODE_DEAD_HOURS
        sort_text = "S to sort by groups"
    
    console.print(sort_text, style="primary", justify="center")
    console.print("←→ to navigate", style="warning", justify="center")
    console.print("ESC to leave\nQ to quit", style="accent", justify="center")


def navigate_schedules(schedules: list[dict], parsed_classes: dict, start_hour: int, end_hour: int, 
                      group_schedule: dict = None, subgroup_schedule: dict = None) -> None:
    """
    Allow the user to navigate between schedules.
    
    Args:
        schedules: List of schedules
        parsed_classes: Parsed class data
        start_hour: Minimum hour to display
        end_hour: Maximum hour to display
        group_schedule: Optional group schedule data for sorting
        subgroup_schedule: Optional subgroup schedule data for sorting
    """
    if not schedules:
        console.print("No schedules found.", style="error", justify="center")
        clear_screen()
        return
    
    # Initialize state variables
    current_schedules = schedules[:]  # Make a copy to avoid modifying original
    current_sort_mode = SORT_MODE_GROUPS  # Default sort mode
    total = len(current_schedules)
    current_index = 0
    grid_view = True
    subject_colors = {subject: SUBJECT_COLORS[i % len(SUBJECT_COLORS)] 
                      for i, subject in enumerate(sorted({s for sched in current_schedules for s in sched.get("subjects", {})}))}
    
    display_interface_schedule_with_sort(current_index, total, current_schedules, parsed_classes, 
                                       start_hour, end_hour, subject_colors, grid_view, current_sort_mode)
    
    while is_interactive_mode():
        key = msvcrt.getwch()
        if key == " ":
            webbrowser.open(current_schedules[current_index]["url"])
        elif key == "\t":
            grid_view = not grid_view
            display_interface_schedule_with_sort(current_index, total, current_schedules, parsed_classes, 
                                                start_hour, end_hour, subject_colors, grid_view, current_sort_mode)
        elif key.lower() == "s":
            # Toggle sort mode
            current_sort_mode = SORT_MODE_DEAD_HOURS if current_sort_mode == SORT_MODE_GROUPS else SORT_MODE_GROUPS
            # Re-sort schedules
            current_schedules = sort_schedules_by_mode(schedules[:], current_sort_mode, group_schedule, subgroup_schedule)
            current_index = 0  # Reset to first schedule after sorting
            display_interface_schedule_with_sort(current_index, total, current_schedules, parsed_classes, 
                                                start_hour, end_hour, subject_colors, grid_view, current_sort_mode)
        elif key == "\xe0":
            code = msvcrt.getwch()
            if code in ("M", "K"):
                current_index = (current_index + 1 if code == "M" else current_index - 1) % total
                display_interface_schedule_with_sort(current_index, total, current_schedules, parsed_classes, 
                                                   start_hour, end_hour, subject_colors, grid_view, current_sort_mode)
        elif key.lower() == "q":
            show_cursor()
            sys.exit(0)
        elif key == "\x1b":
            break
    
    clear_screen()


def display_splash_screen() -> None:
    """Display the FIB Manager splash screen."""
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


def display_subjects_list(quad: str, lang: str) -> None:
    """
    Display a list of subjects for a quadrimester.
    
    Args:
        quad: Quadrimester code
        lang: Language code
    """
    from app.api import fetch_classes_data, fetch_subject_names
    
    clear_screen()
    raw_data = fetch_classes_data(quad, lang)
    parsed_data = parse_classes_data(raw_data)
    names = fetch_subject_names(lang)
    
    total = len(parsed_data)

    header = Text("Subjects ", style="white") + Text(f"{total}", style="#FF5555")
    console.rule(header, style="accent")
    console.print()

    year, quad_num = quad.split("Q")
    ordinal = "1st" if quad_num == "1" else "2nd" if quad_num == "2" else f"{quad_num}th"

    table = Table(title=f"Subjects of the {ordinal} quarter of {year}", header_style="bright_red")
    table.add_column("Code", justify="right", style="bright_black", header_style="bold")
    table.add_column("Name", style="white", header_style="bold")
    
    for subject in sorted(parsed_data.keys()):
        table.add_row(subject, names.get(subject, subject))
    
    console.print(Align(table, align="center"))
    console.print(Align(Text("\nESC to leave\nQ to quit", style="accent", justify="center"), align="center"))
    
    while True:
        key = msvcrt.getwch()
        if key == "\x1b":
            show_cursor()
            clear_screen()
            break
        elif key.lower() == "q":
            show_cursor()
            sys.exit(0)


def display_marks_results(formula: str, values: dict, target: float, solution: dict, result: float) -> None:
    """
    Display marks calculation results in a table format.
    
    Args:
        formula: The formula used for calculation
        values: Dictionary of known variable values
        target: Target result value
        solution: Dictionary of calculated missing variable values
        result: Current result with known values
    """
    clear_screen()
    hide_cursor()
    
    header = Text("Marks Calculator", style="accent")
    console.rule(header, style="accent")
    console.print()
    
    # Formula and target table
    formula_table = Table(title="Formula Information", header_style="secondary")
    formula_table.add_column("Formula", style="white", header_style="bold")
    formula_table.add_column("Target", justify="right", style="white", header_style="bold")
    formula_table.add_column("Current Result", justify="right", style="white", header_style="bold")
    formula_table.add_row(
        formula,
        str(round(target, 2)),
        str(round(result, 2))
    )
    console.print(formula_table, justify="center")
    console.print()
    
    # Known values table
    if values:
        known_table = Table(title="Known Variables", header_style="secondary")
        known_table.add_column("Variable", style="white", header_style="bold")
        known_table.add_column("Value", justify="right", style="white", header_style="bold")
        
        for var, val in sorted(values.items()):
            known_table.add_row(var, str(round(val, 2)))
        
        console.print(known_table, justify="center")
        console.print()
    
    # Solution table
    if solution:
        solution_table = Table(title="Calculated Variables", header_style="secondary")
        solution_table.add_column("Variable", style="white", header_style="bold")
        solution_table.add_column("Value", justify="right", style="accent", header_style="bold")
        
        for var, val in sorted(solution.items()):
            solution_table.add_row(var, str(round(val, 2)))
        
        console.print(solution_table, justify="center")
        console.print()
    
    console.print("\nESC to leave\nQ to quit", style="accent", justify="center")
    
    while True:
        key = msvcrt.getwch()
        if key == "\x1b":
            show_cursor()
            clear_screen()
            break
        elif key.lower() == "q":
            show_cursor()
            sys.exit(0)
