"""
Search module for finding and processing schedules.
"""

import json
import sys

from app.core.utils import parse_blacklist
from app.api import fetch_classes_data
from app.core.parser import parse_classes_data
from app.core.schedule_generator import get_schedule_combinations

def perform_schedule_search(
    quad: str, 
    subjects: list[str], 
    start_hour: int, 
    end_hour: int, 
    languages: list[str], 
    same_subgroup: bool, 
    relax_days: int,
    blacklisted: list[str], 
    show_interface: bool = False
) -> tuple:
    """
    Perform a schedule search.
    
    Args:
        quad: Quadrimester code
        subjects: List of subject codes
        start_hour: Minimum allowed hour
        end_hour: Maximum allowed hour
        languages: List of allowed languages
        same_subgroup: Whether subgroups must match groups
        relax_days: Number of days to relax the schedule by
        blacklisted: List of blacklisted groups
        show_interface: Whether to show an interface
    
    Returns:
        Tuple of (search_result, parsed_data)
    """
    subjects = [s.upper() for s in subjects]
    blacklist_parsed = parse_blacklist(blacklisted)
    
    raw_data = fetch_classes_data(quad, "en")
    parsed_data = parse_classes_data(raw_data)
    
    search_result = get_schedule_combinations(
        quad, subjects, start_hour, end_hour, languages, same_subgroup, relax_days, 
        blacklist_parsed, show_interface
    )
    
    return search_result, parsed_data


def print_json(data: dict) -> None:
    """
    Print data as JSON.
    
    Args:
        data: Data to print
    """
    formatted = json.dumps(data, indent=2)
    if sys.stdout.isatty():
        print(formatted)
    else:
        sys.stdout.write(formatted)
