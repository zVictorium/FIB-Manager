"""
Search module for finding and processing schedules.
"""

import json
import sys
from argparse import ArgumentParser, Namespace

from app.core.utils import normalize_languages, parse_blacklist, parse_whitelist
from app.core.constants import SORT_MODE_GROUPS, SORT_MODE_DEAD_HOURS
from app.api import fetch_classes_data
from app.core.parser import parse_classes_data
from app.core.schedule_generator import get_schedule_combinations
from app.ui.ui import navigate_schedules, check_windows_interactive


def add_search_arguments(parser: ArgumentParser, default_quad: str) -> None:
    """
    Add arguments for the schedules command.
    
    Args:
        parser: ArgumentParser object
        default_quad: Default quadrimester code
    """
    parser.add_argument("-q", "--quadrimester", default=default_quad, 
                        help=f"quadrimester code (e.g., {default_quad})")
    parser.add_argument("-s", "--subjects", nargs="+", required=True, 
                        help="list of subject codes")
    parser.add_argument("--start", type=int, default=8, 
                        help="start hour (inclusive)")
    parser.add_argument("--end", type=int, default=20, 
                        help="end hour (exclusive)")
    parser.add_argument("-l", "--languages", nargs="*", default=[], 
                        help="preferred class languages (e.g., en, es, ca)")
    parser.add_argument("--freedom", action="store_true", 
                        help="allow different subgroup than group")
    parser.add_argument("--days", type=int, default=5, 
                        help="maximum number of days with classes")
    parser.add_argument("--blacklist", nargs="*", default=[],
                        help="blacklisted groups (e.g., IES-10)")
    parser.add_argument("--whitelist", nargs="*", default=[],
                        help="whitelisted groups that must be included (e.g., IES-10, FM-11)")
    parser.add_argument("--max-dead-hours", type=int, default=-1,
                        help="maximum number of dead hours allowed (-1 for no limit)")
    parser.add_argument("--sort", choices=["groups", "dead_hours"], default="groups",
                        help="sort schedules by number of groups or dead hours (default: groups)")
    parser.add_argument("-v", "--view", action="store_true", 
                        help="show search results in interactive interface")


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


def handle_search_command(args: Namespace) -> None:
    """
    Handle the schedules command.
    
    Args:
        args: ArgumentParser arguments
    """
    # Process and normalize input parameters
    normalized_languages = normalize_languages(args.languages)
    max_days = args.days
    relax_days = 5 - max_days
    freedom = args.freedom
    same_subgroup = not freedom
    max_dead_hours = args.max_dead_hours
      # Perform the schedule search
    result, classes, group_schedule, subgroup_schedule = perform_schedule_search(
        args.quadrimester, args.subjects, args.start, args.end,
        normalized_languages, same_subgroup, relax_days,
        args.blacklist, args.whitelist, max_dead_hours, args.view
    )
    
    # Display results in GUI or print JSON
    if args.view:
        if not check_windows_interactive():
            return
        navigate_schedules(result.get("schedules", []), classes, args.start, args.end, 
                          group_schedule, subgroup_schedule)
    else:
        print_json(result)


def perform_schedule_search(
    quad: str, 
    subjects: list[str], 
    start_hour: int, 
    end_hour: int, 
    languages: list[str], 
    same_subgroup: bool, 
    relax_days: int,
    blacklisted: list[str],
    whitelisted: list[str] = None,
    max_dead_hours: int = -1,
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
        whitelisted: List of whitelisted groups that must be included
        max_dead_hours: Maximum allowed dead hours (-1 for no limit)
        show_interface: Whether to show an interface
    
    Returns:
        Tuple of (search_result, parsed_data, group_schedule, subgroup_schedule)
    """
    # Normalize input data
    normalized_subjects = [s.upper() for s in subjects]
    blacklist_parsed = parse_blacklist(blacklisted)
    whitelist_parsed = parse_whitelist(whitelisted or [])
    
    # Fetch and parse class data
    raw_data = fetch_classes_data(quad, "en")
    parsed_data = parse_classes_data(raw_data)
    
    # Split schedule data for sorting functionality
    from app.core.parser import split_schedule_by_group_type
    group_schedule, subgroup_schedule = split_schedule_by_group_type(parsed_data)
    
    # Generate schedule combinations
    search_result = get_schedule_combinations(
        quad, normalized_subjects, start_hour, end_hour, languages, same_subgroup, relax_days, 
        blacklist_parsed, whitelist_parsed, max_dead_hours, show_interface
    )
    
    return search_result, parsed_data, group_schedule, subgroup_schedule
