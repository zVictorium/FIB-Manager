"""
Interactive mode module for selecting options and running the application.
"""

from datetime import date
from typing import Dict, List, Tuple, Any

import questionary
from rich.console import Console

from app.core.constants import SUBJECT_COLORS
from app.api import fetch_classes_data, fetch_subject_names
from app.core.parser import parse_classes_data
from app.core.utils import clear_screen, normalize_language
from app.ui.ui import (
    QUESTIONARY_STYLE, 
    display_splash_screen, 
    display_subjects_list, 
    navigate_schedules
)

console = Console()

def select_year() -> int:
    """
    Prompt the user to select a year.
    
    Returns:
        The selected year
    """
    current_year = date.today().year
    choices = [str(current_year-1), str(current_year), str(current_year+1)]
    selection = questionary.select(
        "Select Year:", 
        choices=choices, 
        instruction="(Use ↑↓ and Enter)", 
        style=QUESTIONARY_STYLE
    ).ask()
    return int(selection)


def select_quadrimester() -> str:
    """
    Prompt the user to select a quadrimester.
    
    Returns:
        The selected quadrimester
    """
    return questionary.select(
        "Select Quadrimester:", 
        choices=["1", "2"], 
        instruction="(Use ↑↓ and Enter)", 
        style=QUESTIONARY_STYLE
    ).ask()


def select_language() -> str:
    """
    Prompt the user to select a language.
    
    Returns:
        The selected language code
    """
    choice = questionary.select(
        "Select language:", 
        choices=["English", "Spanish", "Catalan"],
        instruction="(Use ↑↓ and Enter)", 
        style=QUESTIONARY_STYLE,
        use_jk_keys=False, 
        use_search_filter=True
    ).ask()
    return normalize_language(choice)


def get_group_choices(parsed_data: dict, subjects: list[str]) -> list[str]:
    """
    Get the available group choices for blacklisting.
    
    Args:
        parsed_data: Parsed class data
        subjects: List of subject codes
    
    Returns:
        List of group choices
    """
    choices = []
    for subject in subjects:
        subj = subject.upper()
        for group in parsed_data.get(subj, {}):
            if group.isdigit():
                choices.append(f"{subj}-{group}")
    return sorted(choices)


def select_search_params() -> tuple:
    """
    Interactive selection of search parameters.
    
    Returns:
        Tuple of search parameters
    """
    year = select_year()
    quad_num = select_quadrimester()
    quad = f"{year}Q{quad_num}"
    
    start_hour = int(questionary.select(
        "Start hour:", 
        choices=[str(h) for h in range(8, 21)],
        instruction="(Use ↑↓ and Enter)", 
        style=QUESTIONARY_STYLE,
        use_jk_keys=False, 
        use_search_filter=True
    ).ask())
    
    end_hour = int(questionary.select(
        "End hour:", 
        choices=[str(h) for h in range(start_hour+1, 22)],
        instruction="(Use ↑↓ and Enter)", 
        style=QUESTIONARY_STYLE,
        use_jk_keys=False, 
        use_search_filter=True
    ).ask())
    
    days = int(questionary.select(
        "Maximum days with classes:", 
        choices=[str(i) for i in range(1, 6)],
        default="5", 
        instruction="(Use ↑↓ and Enter)", 
        style=QUESTIONARY_STYLE,
        use_jk_keys=False, 
        use_search_filter=True
    ).ask())
    
    relax_days = 5 - days
    
    freedom = questionary.select(
        "Allow different subgroup than group?",
        choices=["Yes", "No"], 
        instruction="(Use ↑↓ and Enter)",
        style=QUESTIONARY_STYLE, 
        use_jk_keys=False
    ).ask() == "Yes"
    
    same_subgroup = not freedom
    
    languages_native = questionary.checkbox(
        "Select languages of the classes:",
        choices=["English", "Spanish", "Catalan"],
        instruction="(Use ↑↓, Space toggle and Enter)",
        style=QUESTIONARY_STYLE, 
        validate=lambda ans: True if ans else "Select at least one",
        use_jk_keys=False, 
        use_search_filter=True
    ).ask()
    
    languages = [normalize_language(l) for l in languages_native]
    
    raw_data = fetch_classes_data(quad, "en")
    parsed_data = parse_classes_data(raw_data)
    names = fetch_subject_names("en")
    
    subject_choices = [f"{code} - {names.get(code, code)}" for code in sorted(parsed_data.keys())]
    
    subjects_selected = questionary.checkbox(
        "Select subjects:", 
        choices=subject_choices,
        instruction="(Use ↑↓, Space toggle and Enter)",
        style=QUESTIONARY_STYLE, 
        validate=lambda ans: True if ans else "Select at least one",
        use_jk_keys=False, 
        use_search_filter=True
    ).ask()
    
    subjects = [item.split(" - ", 1)[0].upper() for item in subjects_selected]
    
    blacklist_choices = get_group_choices(parsed_data, subjects)
    
    blacklisted = questionary.checkbox(
        "Blacklisted groups:", 
        choices=blacklist_choices,
        instruction="(Use ↑↓, Space toggle and Enter)", 
        style=QUESTIONARY_STYLE,
        use_jk_keys=False, 
        use_search_filter=True
    ).ask()
    
    return quad, subjects, start_hour, end_hour, languages, blacklisted, same_subgroup, relax_days


def display_subjects_for_selection() -> None:
    """Display subjects list with interactive selection."""
    year = select_year()
    quad_num = select_quadrimester()
    quad = f"{year}Q{quad_num}"
    lang_choice = select_language()
    display_subjects_list(quad, lang_choice)


def perform_app_search() -> None:
    """Perform a schedule search from the app interface."""
    from app.commands.search import perform_schedule_search
    
    quad, subjects, start_hour, end_hour, languages, blacklisted, same_subgroup, relax_days = select_search_params()
    clear_screen()
    result, parsed_data = perform_schedule_search(
        quad, subjects, start_hour, end_hour, languages,
        same_subgroup, relax_days, blacklisted, True
    )
    schedules = result.get("schedules", [])
    
    if not schedules:
        console.print("No schedules found.", style="error", justify="center")
    else:
        navigate_schedules(schedules, parsed_data, start_hour, end_hour)


def run_interactive_app() -> None:
    """Run the interactive application."""
    import sys
    import traceback
    
    try:
        print("Displaying splash screen...")
        display_splash_screen()
        
        while True:
            try:
                clear_screen()
                option = questionary.select(
                    "Select option:", 
                    choices=["Search schedules", "List subjects", "Quit"],
                    instruction="(Use ↑↓ and Enter)", 
                    style=QUESTIONARY_STYLE,
                    use_jk_keys=False, 
                    use_search_filter=True
                ).ask()
                
                clear_screen()
                
                if option in ("Quit", None):
                    sys.exit(0)
                elif option == "List subjects":
                    display_subjects_for_selection()
                elif option == "Search schedules":
                    perform_app_search()
            except Exception as e:
                print(f"Error in interactive menu: {e}")
                traceback.print_exc()
                input("Press Enter to continue...")
    except Exception as e:
        print(f"Fatal error in interactive app: {e}")
        traceback.print_exc()
