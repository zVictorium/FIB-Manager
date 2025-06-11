"""
Main command-line interface for FIB Manager.
"""

import sys
import json
from argparse import ArgumentParser, Namespace

from app.core.utils import get_default_quadrimester
from app.ui.interactive import run_interactive_app
from app.ui.ui import check_windows_interactive
from app.commands.search import add_search_arguments, handle_search_command
from app.commands.subjects import add_subjects_arguments, handle_subjects_command
from app.commands.marks import add_marks_arguments, handle_marks_command

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


def handle_app_command(args: Namespace) -> None:
    """
    Handle the app command.
    
    Args:
        args: ArgumentParser arguments
    """
    # Set console title on Windows
    import os
    if os.name == 'nt':  # Windows
        os.system('title FIB Manager')
    
    if not check_windows_interactive():
        return
    
    try:
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
    
    # Marks command
    marks_parser = subparsers.add_parser("marks", help="manage subject marks")
    add_marks_arguments(marks_parser)
    
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
        elif args.command == "marks":
            handle_marks_command(args)
        elif args.command == "app":
            handle_app_command(args)
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
