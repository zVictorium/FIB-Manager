"""
Subjects command module for FIB Manager.
"""

import json
import sys
from argparse import ArgumentParser, Namespace

from app.core.utils import normalize_language
from app.core.parser import parse_classes_data
from app.api import fetch_classes_data, fetch_subject_names
from app.ui.ui import display_subjects_list, check_windows_interactive


def add_subjects_arguments(parser: ArgumentParser, default_quad: str) -> None:
    """
    Add arguments for the subjects command.
    
    Args:
        parser: ArgumentParser object
        default_quad: Default quadrimester code
    """
    parser.add_argument("-q", "--quadrimester", default=default_quad, 
                      help=f"quadrimester code (e.g., {default_quad})")
    parser.add_argument("-l", "--language", default="en", 
                      help="language code for subject names (e.g., en, es, ca)")
    parser.add_argument("-v", "--view", action="store_true", 
                      help="display subjects in interactive interface")


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


def handle_subjects_command(args: Namespace) -> None:
    """
    Handle the subjects command.
    
    Args:
        args: ArgumentParser arguments
    """
    # Normalize language input
    normalized_lang = normalize_language(args.language)
    
    # Fetch and parse subject data
    raw_data = fetch_classes_data(args.quadrimester, normalized_lang)
    parsed_data = parse_classes_data(raw_data)
    names = fetch_subject_names(normalized_lang)
    
    # Create sorted dictionary of subjects with names
    subjects = {
        subject: names.get(subject, subject) 
        for subject in sorted(parsed_data.keys())
    }
    
    # Prepare result data
    subjects_data = {
        "quadrimester": args.quadrimester,
        "language": normalized_lang,
        "subjects": subjects
    }
    
    # Display results in GUI or print JSON
    if args.view:
        if not check_windows_interactive():
            return
        display_subjects_list(args.quadrimester, normalized_lang)
    else:
        print_json(subjects_data)
