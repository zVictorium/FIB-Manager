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

# Consolidated map for language normalization
LANGUAGE_MAP = {
    "catala": "ca", "català": "ca", "catalan": "ca", "ca": "ca",
    "castella": "es", "castellà": "es", "castellano": "es", "espanol": "es", "español": "es", "spanish": "es", "es": "es",
    "english": "en", "anglés": "en", "angles": "en", "inglés": "en", "ingles": "en", "en": "en",
}


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
    parser = ArgumentParser(prog="schedule-searcher")
    subparsers = parser.add_subparsers(dest="command")

    # Search command
    search = subparsers.add_parser("search", help="Search for schedule combinations")
    search.add_argument("--debug", action="store_true", help="Enable debug output")
    search.add_argument("--quad", default=default_quad, help=f"Quadrimester code, e.g., {default_quad}")
    search.add_argument("--subjects", nargs="+", required=True, help="List of subject codes")
    search.add_argument("--start-hour", type=int, default=8, help="Start hour (inclusive)")
    search.add_argument("--end-hour", type=int, default=20, help="End hour (exclusive)")
    search.add_argument("--languages", nargs="*", default=[], help="Preferred class languages")
    search.add_argument("--same-subgroup-as-group", action="store_true",
                         help="Require subgroup tens match group")
    search.add_argument("--relax-days", type=int, default=0, help="Number of relaxable off-days")
    search.add_argument("--blacklisted", nargs="*", default=[], help="Blacklisted subject-group pairs, e.g., IES-101")
    search.add_argument("--lang", default="en", help="Language code for subject names and API (e.g., en, es, ca)")

    # Subjects command
    subjects = subparsers.add_parser("subjects", help="Show all available subjects for a quad")
    subjects.add_argument("-q", "--quad", default=default_quad,
                          help=f"Quadrimester code, e.g., {default_quad}")
    subjects.add_argument("-l", "--lang", default="en",
                          help="Language code for subject names (e.g., en, es, ca)")

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
    print(json.dumps(result, indent=2, ensure_ascii=False))


def handle_subjects(args: Namespace) -> None:
    """Process the 'subjects' command."""
    lang = LANGUAGE_MAP.get(args.lang.lower(), args.lang)
    raw = fetch_classes_data_with_language(args.quad, lang)
    parsed = parse_classes_data(raw)
    names = fetch_subject_names(lang)
    for subj in sorted(parsed.keys()):
        print(f"{subj}: {names.get(subj, subj)}")


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
    else:
        handle_subjects(args)


if __name__ == "__main__":
    main()
