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
    
    max_dead_hours_choice = questionary.select(
        "Maximum dead hours allowed:", 
        choices=["No limit", "0", "1", "2", "3", "4", "5"],
        default="No limit", 
        instruction="(Use ↑↓ and Enter)", 
        style=QUESTIONARY_STYLE,
        use_jk_keys=False, 
        use_search_filter=True
    ).ask()
    
    # Convert "No limit" to -1, otherwise convert to int
    if max_dead_hours_choice == "No limit":
        max_dead_hours = -1
    else:
        max_dead_hours = int(max_dead_hours_choice)
    
    return quad, subjects, start_hour, end_hour, languages, blacklisted, same_subgroup, relax_days, max_dead_hours


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
    
    quad, subjects, start_hour, end_hour, languages, blacklisted, same_subgroup, relax_days, max_dead_hours = select_search_params()
    clear_screen()
    result, parsed_data, group_schedule, subgroup_schedule = perform_schedule_search(
        quad, subjects, start_hour, end_hour, languages,
        same_subgroup, relax_days, blacklisted, max_dead_hours, True
    )
    schedules = result.get("schedules", [])
    
    if not schedules:
        console.print("No schedules found.", style="error", justify="center")
    else:
        navigate_schedules(schedules, parsed_data, start_hour, end_hour, group_schedule, subgroup_schedule)


def perform_marks_calculation() -> None:
    """Perform a marks calculation from the app interface."""
    from app.commands.marks import (
        find_variable_names, 
        get_missing_variables, 
        solve_for_missing_variables, 
        calculate_baseline_result,
        process_marks_calculation
    )
    from app.ui.ui import display_marks_results, check_windows_interactive
    
    # Early return if not in interactive mode
    if not check_windows_interactive():
        return
    
    clear_screen()
    
    try:
        # Get formula from user
        formula = questionary.text(
            "Enter formula (e.g., EX1 * 0.4 + EX2 * 0.6):",
            instruction="Use variable names for marks",
            style=QUESTIONARY_STYLE,
            validate=lambda text: bool(text.strip())
        ).ask()
        
        if not formula:
            return
        
        # Get target mark
        target_text = questionary.text(
            "Enter target mark (e.g., 5.0):",
            instruction="The minimum mark you want to achieve",
            style=QUESTIONARY_STYLE,
            validate=lambda text: text.replace('.', '', 1).isdigit() and 0 <= float(text) <= 10
        ).ask()
        
        if not target_text:
            return
        
        target = float(target_text)
          # Find variables in formula
        variables = find_variable_names(formula)
        
        # Get known variable values from user
        values = {}
        for var in variables:
            known = questionary.confirm(
                f"Do you know the value for {var}?",
                style=QUESTIONARY_STYLE
            ).ask()
            
            if known:
                var_value = questionary.text(
                    f"Enter value for {var}:",
                    instruction="Enter a number from 0 to 10",
                    style=QUESTIONARY_STYLE,
                    validate=lambda text: text.replace('.', '', 1).isdigit() and 0 <= float(text) <= 10
                ).ask()
                
                if var_value:
                    values[var] = float(var_value)
        
        # Process the calculation using the shared helper function
        values, result, solution = process_marks_calculation(formula, values, target)
        
        # Display results
        display_marks_results(formula, values, target, solution, result)
    except Exception as e:
        console.print(f"Error in marks calculation: {str(e)}", style="error", justify="center")
        import traceback
        traceback.print_exc()
        input("Press Enter to continue...")


def run_interactive_app() -> None:
    """Run the interactive application."""
    import sys
    import traceback
    
    try:
        display_splash_screen()
        
        while True:
            try:
                clear_screen()
                option = questionary.select(
                    "Select option:", 
                    choices=["Search schedules", "List subjects", "Calculate marks", "Quit"],
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
                elif option == "Calculate marks":
                    perform_marks_calculation()
            except Exception as e:
                pass
                # print(f"Error in interactive menu: {e}")
                # traceback.print_exc()
                # input("Press Enter to continue...")
    except Exception as e:
        pass
        # print(f"Fatal error in interactive app: {e}")
        # traceback.print_exc()
