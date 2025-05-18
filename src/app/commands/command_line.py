"""
Main command-line interface for FIB Manager.
"""

import sys
import json
from argparse import ArgumentParser, Namespace

from app.core.utils import get_default_quadrimester, normalize_languages, normalize_language
from app.core.parser import parse_classes_data
from app.api import fetch_classes_data, fetch_subject_names
from app.core.constants import LANGUAGE_MAPPING
from app.ui.ui import navigate_schedules, display_subjects_list, check_windows_interactive
from app.ui.interactive import run_interactive_app
from app.commands.search import perform_schedule_search

def add_search_arguments(parser: ArgumentParser, default_quad: str) -> None:
    """
    Add arguments for the schedules command.
    
    Args:
        parser: ArgumentParser object
        default_quad: Default quadrimester code
    """
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
    """
    Add arguments for the subjects command.
    
    Args:
        parser: ArgumentParser object
        default_quad: Default quadrimester code
    """
    parser.add_argument("-q", "--quadrimester", default=default_quad, help=f"quadrimester code (e.g., {default_quad})")
    parser.add_argument("-l", "--language", default="en", help="language code for subject names (e.g., en, es, ca)")
    parser.add_argument("-v", "--view", action="store_true", help="display subjects in interactive interface")


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
    args.languages = normalize_languages(args.languages)
    max_days = args.days
    relax_days = 5 - max_days
    freedom = args.freedom
    same_subgroup = not freedom
    
    result, classes = perform_schedule_search(
        args.quadrimester, args.subjects, args.start, args.end,
        args.languages, same_subgroup, relax_days,
        args.blacklist, args.view
    )
    
    if args.view:
        if not check_windows_interactive():
            return
        navigate_schedules(result.get("schedules", []), classes, args.start, args.end)
    else:
        print_json(result)


def handle_subjects_command(args: Namespace) -> None:
    """
    Handle the subjects command.
    
    Args:
        args: ArgumentParser arguments
    """
    lang = normalize_language(args.language)
    raw_data = fetch_classes_data(args.quadrimester, lang)
    parsed_data = parse_classes_data(raw_data)
    names = fetch_subject_names(lang)
    subjects = {subject: names.get(subject, subject) for subject in sorted(parsed_data.keys())}
    subjects_data = {
        "quadrimester": args.quadrimester,
        "language": lang,
        "subjects": subjects
    }
    
    if args.view:
        if not check_windows_interactive():
            return
        display_subjects_list(args.quadrimester, lang)
    else:
        print_json(subjects_data)


def handle_app_command(args: Namespace) -> None:
    """
    Handle the app command.
    
    Args:
        args: ArgumentParser arguments
    """
    if not check_windows_interactive():
        return
    
    try:
        print("Starting interactive app...")
        run_interactive_app()
    except Exception as e:
        print(f"Error running interactive app: {e}")
        import traceback
        traceback.print_exc()


def build_argument_parser(default_quad: str) -> ArgumentParser:
    """
    Build the argument parser for the command-line interface.
    
    Args:
        default_quad: Default quadrimester code
    
    Returns:
        ArgumentParser object
    """
    parser = ArgumentParser(prog="fib-manager")
    subparsers = parser.add_subparsers(dest="command")
    
    # Interactive application command
    subparsers.add_parser("app", help="start interactive application")
    
    # Schedule search command
    schedules_parser = subparsers.add_parser("schedules", help="search schedule combinations")
    add_search_arguments(schedules_parser, default_quad)
    
    # Subjects list command
    subjects_parser = subparsers.add_parser("subjects", help="show subjects for a quadrimester")
    add_subjects_arguments(subjects_parser, default_quad)
    
    return parser


def main() -> None:
    """Main entry point for the command-line interface."""
    try:
        default_quad = get_default_quadrimester()
        parser = build_argument_parser(default_quad)
        args = parser.parse_args()
        
        if args.command == "schedules":
            handle_search_command(args)
        elif args.command == "subjects":
            handle_subjects_command(args)
        elif args.command == "app":
            print("Starting interactive app mode...")
            handle_app_command(args)
        else:
            parser.print_help()
    except:
        pass


if __name__ == "__main__":
    main()
