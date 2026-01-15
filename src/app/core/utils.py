"""
Utility functions for the FIB Manager application.
"""

import os
import sys
import time
import shutil
import threading
from datetime import date

# Import msvcrt only on Windows
try:
    import msvcrt
except ImportError:
    msvcrt = None
from typing import Dict, List, Any
from rich.console import Console
from rich.text import Text

from app.core.constants import FILLED_BAR_COLOR, EMPTY_BAR_COLOR, TEXT_COLOR, NUMBER_COLOR, LANGUAGE_MAP

console = Console()

def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def hide_cursor() -> None:
    """Hide the terminal cursor."""
    if sys.stdout.isatty():
        print("\033[?25l", end="", flush=True)


def show_cursor() -> None:
    """Show the terminal cursor."""
    if sys.stdout.isatty():
        print("\033[?25h", end="", flush=True)


def is_interactive_mode() -> bool:
    """Check if the terminal is in interactive mode."""
    try:
        return sys.stdout.isatty()
    except NameError:
        return False


def get_default_quadrimester() -> str:
    """
    Get the default quadrimester based on the current date.
    
    Returns:
        Quadrimester code in the format YYYYQ#
    """
    today = date.today()
    half = 1 if today.month <= 6 else 2
    return f"{today.year-1}Q{half+1}"


def normalize_language(lang: str) -> str:
    """
    Normalize a language name to its code.
    
    Args:
        lang: Language name or code
    
    Returns:
        Normalized language code
    """
    return LANGUAGE_MAP.get(lang.lower(), lang)


def normalize_languages(langs: list[str]) -> list[str]:
    """
    Normalize a list of language names to their codes.
    
    Args:
        langs: List of language names or codes
    
    Returns:
        List of normalized language codes
    """
    return [normalize_language(l) for l in langs]


def parse_blacklist(blacklist_items: list[str]) -> list[list[str, int]]:
    """
    Parse a list of blacklisted groups.
    
    Args:
        blacklist_items: List of blacklisted groups in the format "SUBJECT-GROUP"
    
    Returns:
        List of [subject, group] pairs
    """
    parsed = []
    for item in blacklist_items:
        if "-" not in item:
            continue
        subject, group = item.split("-", 1)
        if not group.isdigit():
            continue
        parsed.append([subject.upper(), int(group)])
    return parsed


def update_terminal_progress(count: int, total: int) -> None:
    """
    Update the progress bar in the terminal.
    
    Args:
        count: Current progress
        total: Total progress
    """
    if not sys.stdout.isatty():
        return
    if hasattr(update_terminal_progress, "last_count") and update_terminal_progress.last_count == count:
        return
    update_terminal_progress.last_count = count

    now = time.monotonic()
    if hasattr(update_terminal_progress, "last_time") and count != total:
        if now - update_terminal_progress.last_time < 0.1:
            return
    update_terminal_progress.last_time = now

    if not hasattr(update_terminal_progress, "position_set"):
        os.system("cls" if os.name == "nt" else "clear")
    print("\033[?25l", end="", flush=True)
    
    size = shutil.get_terminal_size()
    bar_width = min(50, max(size.columns - 10, 10))
    filled = int(bar_width * count / total) if total else bar_width
    bar = Text("│", style=TEXT_COLOR) + Text("█" * filled, style=FILLED_BAR_COLOR) + \
          Text("░" * (bar_width - filled), style=EMPTY_BAR_COLOR) + Text("│", style=TEXT_COLOR)
    count_text = Text(f"{count}", style=NUMBER_COLOR) + Text("/", style=TEXT_COLOR) + Text(f"{total}", style=NUMBER_COLOR)

    if not hasattr(update_terminal_progress, "position_set"):
        top_padding = max((size.lines - 2) // 2, 0)
        print("\033[H" + "\n" * top_padding, end="")
        update_terminal_progress.position_set = True
    else:
        print("\033[2A", end="")

    print("\033[2K", end="")  # clear line
    console.print(bar, justify="center")
    print("\033[2K", end="")
    console.print(count_text, justify="center")
    if count == total:
        print("\033[?25h", end="", flush=True)


def run_progress_thread(progress: Dict[str, Any]) -> None:
    """
    Run a thread to update the progress bar.
    
    Args:
        progress: Dictionary with 'count', 'total', and 'done' keys
    """
    if not sys.stdout.isatty():
        return
    last = -1
    while not progress["done"]:
        if progress["count"] != last:
            update_terminal_progress(progress["count"], progress["total"])
            last = progress["count"]
        time.sleep(0.1)
    update_terminal_progress(progress["total"], progress["total"])
