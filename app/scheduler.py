import requests
import itertools
import logging
import os
import shutil
import threading
import time
from typing import Any, Dict, List, Tuple, Set
from rich.console import Console
from rich.text import Text

# Initialize module logger
logger = logging.getLogger(__name__)

API_BASE_URL = "https://api.fib.upc.edu/v2"
CLIENT_ID = "77qvbbQqni4TcEUsWvUCKOG1XU7Hr0EfIs4pacRz"
LANGUAGE_MAPPING = {"en": "en", "es": "es", "ca": "ca", "": "en"}
DEFAULT_LANGUAGE = "ca"

console = Console()

# UI Theme colors
FILLED_BAR_COLOR = "#FF5555 bold"  # accent/highlighted color
EMPTY_BAR_COLOR = "#666666 bold"   # secondary color
TEXT_COLOR = "#666666 bold"        # primary color


def fetch_api_data(url: str, language: str) -> Dict[str, Any]:
    """Fetch data from API with proper language headers."""
    headers = {"Accept-Language": language}
    logger.debug(f"Requesting data: {url}")
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logger.error(f"Failed to fetch data: HTTP {response.status_code}")
        return {"results": []}
        
    return response.json()


def fetch_paginated_data(base_url: str, language: str) -> List[Dict[str, Any]]:
    """Fetch all data entries from a paginated API endpoint."""
    results = []
    current_url = base_url
    
    while current_url:
        page_data = fetch_api_data(current_url, language)
        results.extend(page_data.get("results", []))
        current_url = page_data.get("next", "")
        
    return results


def fetch_classes_data(quadrimester: str, language: str) -> Dict[str, List[Dict[str, Any]]]:
    """Fetch all class entries for a quadrimester, following pagination."""
    url = f"{API_BASE_URL}/quadrimestres/{quadrimester}/classes.json?client_id={CLIENT_ID}&lang={language}"
    results = fetch_paginated_data(url, language)
    
    logger.debug(f"Total class entries fetched: {len(results)}")
    return {"results": results}


def fetch_subject_names(language: str) -> Dict[str, str]:
    """Fetch code-to-name map for subjects."""
    url = f"{API_BASE_URL}/assignatures.json?format=json&client_id={CLIENT_ID}&lang={language}"
    subjects_data = fetch_paginated_data(url, language)
    
    names = {}
    for item in subjects_data:
        code = item.get("id")
        name = item.get("nom")
        if code and name:
            names[code] = name
            
    logger.debug(f"Total subjects fetched: {len(names)}")
    return names


def extract_class_info(class_info: Dict[str, Any]) -> Dict[str, Any]:
    """Extract relevant information from a class entry."""
    time_parts = class_info.get("inici", "00:00").split(":")
    if len(time_parts) < 2:
        return {}
        
    start_hour = int(time_parts[0])
    duration = class_info.get("durada", 0)
    
    base_info = {
        "type": class_info.get("tipus", ""),
        "classroom": class_info.get("aules", []),
        "language": class_info.get("idioma", ""),
        "day": class_info.get("dia_setmana", 0),
        "group": int(class_info.get("grup", "0")),
    }
    
    entries = []
    for offset in range(duration):
        entry = base_info.copy()
        entry["hour"] = start_hour + offset
        entries.append(entry)
        
    return entries


def is_valid_class_entry(class_info: Dict[str, Any]) -> bool:
    """Check if a class entry has valid data."""
    subject = class_info.get("codi_assig")
    group = class_info.get("grup")
    
    if not subject or not group:
        return False
    
    try:
        int(group)
        return True
    except ValueError:
        return False


def parse_classes_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse raw classes data into a structured format."""
    parsed = {}
    
    for class_info in data.get("results", []):
        if not is_valid_class_entry(class_info):
            continue
            
        subject = class_info.get("codi_assig")
        group_id = class_info.get("grup")
        entries = extract_class_info(class_info)
        
        if not entries:
            continue
            
        parsed.setdefault(subject, {"name": subject})
        group_key = str(group_id)
        parsed[subject].setdefault(group_key, [])
        
        for entry in entries:
            parsed[subject][group_key].append(entry)
    
    add_missing_groups(parsed)
    return parsed


def add_missing_groups(parsed_data: Dict[str, Any]) -> None:
    """Add missing groups and subgroups for consistency."""
    # Add missing subgroups for each main group
    for subject, groups in parsed_data.items():
        main_groups = [g for g in groups.keys() if g.isdigit() and int(g) % 10 == 0]
        for main_group in main_groups:
            subgroup = str(int(main_group) + 1)
            groups.setdefault(subgroup, [])
    
    # Add missing main groups if subgroup exists
    for subject, groups in parsed_data.items():
        subgroups = [int(g) for g in groups.keys() if g.isdigit() and int(g) % 10 != 0]
        for subgroup in subgroups:
            main_group = str(subgroup - (subgroup % 10))
            groups.setdefault(main_group, [])


def get_time_slots(schedule: Dict[str, Any], combo: Dict[str, Any]) -> Dict[Tuple[int, int], List[str]]:
    """Get all occupied time slots for a given schedule combination."""
    slots = {}
    
    for subject, group in combo.items():
        classes = schedule.get(subject, {}).get(str(group), [])
        for class_info in classes:
            slot = (class_info["day"], class_info["hour"])
            slots.setdefault(slot, []).append(subject)
            
    return slots


def get_days_with_classes(slots: Dict[Tuple[int, int], List[str]]) -> Set[int]:
    """Get the set of days that have classes."""
    return {day for day, _ in slots.keys()}


def count_total_days_with_classes(group_slots: Dict[Tuple[int, int], List[str]],
                                 subgroup_slots: Dict[Tuple[int, int], List[str]]) -> int:
    """Count the total number of days with classes."""
    days = get_days_with_classes(group_slots)
    days.update(get_days_with_classes(subgroup_slots))
    return len(days)


def is_language_compatible(class_language: str, allowed_languages: List[str]) -> bool:
    """Check if a class language is compatible with allowed languages."""
    if not class_language or not allowed_languages:
        return True
        
    class_language = class_language.lower()
    return any(lang.lower() in class_language for lang in allowed_languages)


def is_within_time_bounds(hours: Set[int], start_hour: int, end_hour: int) -> bool:
    """Check if all hours are within the specified bounds."""
    if not hours:
        return True
    return min(hours) >= start_hour and max(hours) <= end_hour


def is_group_blacklisted(subject: str, group: str, blacklisted: List[List[Any]]) -> bool:
    """Check if a subject-group combination is blacklisted."""
    return [subject, int(group)] in blacklisted


def is_valid_schedule(schedule: Dict[str, Any],
                     combo: Dict[str, Any],
                     blacklisted: List[List[Any]],
                     languages: List[str],
                     start_hour: int,
                     end_hour: int) -> bool:
    """Check if a schedule is valid according to constraints."""
    used_slots = {}
    hours = set()
    
    for subject, group in combo.items():
        if is_group_blacklisted(subject, group, blacklisted):
            return False
            
        for class_info in schedule.get(subject, {}).get(str(group), []):
            if not is_language_compatible(class_info.get("language", ""), languages):
                return False
                
            slot = (class_info["day"], class_info["hour"])
            if slot in used_slots:
                return False
                
            used_slots[slot] = True
            hours.add(class_info["hour"])
    
    return is_within_time_bounds(hours, start_hour, end_hour)


def has_schedule_conflicts(all_slots: Dict[Tuple[int, int], List[str]]) -> bool:
    """Check if a schedule has conflicts (multiple subjects in same slot)."""
    return any(len(subjects) > 1 for subjects in all_slots.values())


def has_valid_schedule(group_slots: Dict[Tuple[int, int], List[str]],
                      subgroup_slots: Dict[Tuple[int, int], List[str]],
                      max_days: int,
                      start_hour: int,
                      end_hour: int) -> bool:
    """Check if a combined schedule is valid according to all constraints."""
    # Merge all slots
    all_slots = {**{slot: subjects[:] for slot, subjects in group_slots.items()}}
    for slot, subjects in subgroup_slots.items():
        all_slots.setdefault(slot, []).extend(subjects)
    
    # Check for conflicts
    if has_schedule_conflicts(all_slots):
        return False
        
    # Check day constraint
    days_with_classes = count_total_days_with_classes(group_slots, subgroup_slots)
    if days_with_classes > max_days:
        return False
        
    # Check time constraint
    hours = {hour for _, hour in all_slots.keys()} if all_slots else set()
    return is_within_time_bounds(hours, start_hour, end_hour)


def are_groups_in_same_tens(group: int, subgroup: int) -> bool:
    """Check if a group and subgroup are in the same tens."""
    return group // 10 == subgroup // 10


def generate_url(combo: Dict[str, Any], quadrimester: str) -> str:
    """Generate a URL for the given schedule combination."""
    base = "https://www.fib.upc.edu/en/studies/bachelors-degrees/bachelor-degree-informatics-engineering/timetables"
    params = f"?&class=true&lang=true&quad={quadrimester}"
    parts = []
    
    for subject, group_info in combo.items():
        parts.append(f"a={subject}_{group_info['group']}")
        parts.append(f"a={subject}_{group_info['subgroup']}")
        
    return base + params + "&" + "&".join(parts)


def update_progress_display(count: int, total: int) -> None:
    """Update the progress display with current count."""
    # Prevent unnecessary updates by checking if the count has changed
    if hasattr(update_progress_display, "last_count") and update_progress_display.last_count == count:
        return
    update_progress_display.last_count = count
        
    # Throttle updates to avoid excessive refreshing
    now = time.monotonic()
    if hasattr(update_progress_display, "last_time") and count != total:
        if now - update_progress_display.last_time < 0.1:  # Increased throttle time
            return
    update_progress_display.last_time = now
    
    # Clear screen on first display
    if not hasattr(update_progress_display, "position_set"):
        os.system("cls" if os.name == "nt" else "clear")
    
    # Hide cursor during update
    print("\033[?25l", end="", flush=True)
    
    # Get terminal size
    size = shutil.get_terminal_size()
    width, height = size.columns, size.lines
    
    # Build progress bar
    bar_width = min(50, max(width - 10, 10))
    filled = int(bar_width * count / total) if total > 0 else bar_width
    
    # Create styled bar components
    filled_bar = Text("█" * filled, style=FILLED_BAR_COLOR)
    empty_bar = Text("░" * (bar_width - filled), style=EMPTY_BAR_COLOR)
    bar_start = Text("│", style=TEXT_COLOR)
    bar_end = Text("│", style=TEXT_COLOR)
    
    # Combine components
    bar = bar_start + filled_bar + empty_bar + bar_end
    
    # Create header-style count display
    count_text = Text(str(count), style=FILLED_BAR_COLOR)
    separator = Text("/", style=TEXT_COLOR)
    total_text = Text(str(total), style=FILLED_BAR_COLOR)
    formatted_text = count_text + separator + total_text
    
    # Save current position to restore later
    if not hasattr(update_progress_display, "position_set"):
        # Move to center of screen for first display
        top_pad = max((height - 2) // 2, 0)
        print("\033[H", end="")  # Move to top-left
        print("\n" * top_pad, end="")
        update_progress_display.position_set = True
    else:
        # Move cursor up 2 lines to rewrite the progress bar
        print("\033[2A", end="")
    
    # Clear line and write updated content
    print("\033[2K", end="")  # Clear line
    console.print(bar, justify="center")
    print("\033[2K", end="")  # Clear line
    console.print(formatted_text, justify="center")
    
    # Show cursor when complete
    if count == total:
        print("\033[?25h", end="", flush=True)


def run_progress_display(progress: Dict[str, Any]) -> None:
    """Run progress display in a separate thread."""
    last_count = -1  # To track changes
    
    while not progress["done"]:
        current_count = progress["count"]
        # Only update if count changed
        if current_count != last_count:
            update_progress_display(current_count, progress["total"])
            last_count = current_count
        time.sleep(0.1)  # Reduced update frequency
        
    # Final draw
    update_progress_display(progress["total"], progress["total"])


def get_valid_group_combinations(group_schedule: Dict[str, Dict[str, List[Dict[str, Any]]]],
                               subjects: List[str],
                               blacklisted_groups: List[List[Any]],
                               allowed_languages: List[str],
                               start_hour: int,
                               end_hour: int) -> List[Dict[str, str]]:
    """Get all valid group combinations."""
    available_groups = {
        s: list(group_schedule[s].keys()) for s in subjects if s in group_schedule
    }
    logger.debug(f"Available group options per subject: {available_groups}")
    
    all_combinations = [
        dict(zip(available_groups.keys(), prod))
        for prod in itertools.product(*available_groups.values())
    ]
    
    valid_combinations = []
    for combo in all_combinations:
        if is_valid_schedule(
            group_schedule, combo, blacklisted_groups, allowed_languages, start_hour, end_hour
        ):
            valid_combinations.append(combo)
            
    logger.debug(f"Valid group combinations count: {len(valid_combinations)}")
    return valid_combinations


def get_valid_subgroup_combinations(subgroup_schedule: Dict[str, Dict[str, List[Dict[str, Any]]]],
                                  subjects: List[str],
                                  blacklisted_groups: List[List[Any]],
                                  allowed_languages: List[str],
                                  start_hour: int,
                                  end_hour: int) -> List[Dict[str, str]]:
    """Get all valid subgroup combinations."""
    available_subgroups = {
        s: list(subgroup_schedule[s].keys()) for s in subjects if s in subgroup_schedule
    }
    logger.debug(f"Available subgroup options per subject: {available_subgroups}")
    
    all_combinations = [
        dict(zip(available_subgroups.keys(), prod))
        for prod in itertools.product(*available_subgroups.values())
    ]
    
    valid_combinations = []
    for combo in all_combinations:
        if is_valid_schedule(
            subgroup_schedule, combo, blacklisted_groups, allowed_languages, start_hour, end_hour
        ):
            valid_combinations.append(combo)
            
    logger.debug(f"Valid subgroup combinations count: {len(valid_combinations)}")
    return valid_combinations


def merge_valid_schedules(group_combos: List[Dict[str, str]],
                        subgroup_combos: List[Dict[str, str]],
                        group_schedule: Dict[str, Dict[str, List[Dict[str, Any]]]],
                        subgroup_schedule: Dict[str, Dict[str, List[Dict[str, Any]]]],
                        max_days: int,
                        start_hour: int,
                        end_hour: int,
                        same_subgroup_as_group: bool,
                        quadrimester: str,
                        show_progress: bool = False) -> List[Dict[str, Any]]:
    """Merge valid group and subgroup schedules."""
    schedules = []
    urls = []
    
    total_combinations = max(len(group_combos) * len(subgroup_combos), 1)
    progress = {"count": 0, "total": total_combinations, "done": False}

    # Start progress display thread if needed
    thread = None
    if show_progress:
        thread = threading.Thread(target=run_progress_display, args=(progress,), daemon=True)
        thread.start()
    
    # Check all combinations
    for group_combo in group_combos:
        for subgroup_combo in subgroup_combos:
            progress["count"] += 1
            
            group_slots = get_time_slots(group_schedule, group_combo)
            subgroup_slots = get_time_slots(subgroup_schedule, subgroup_combo)
            
            # Skip if schedule is invalid
            if not has_valid_schedule(group_slots, subgroup_slots, max_days, start_hour, end_hour):
                continue
                
            # Skip if groups don't match subgroups when required
            if same_subgroup_as_group and not all(
                are_groups_in_same_tens(
                    int(group_combo[subject]), 
                    int(subgroup_combo.get(subject, group_combo[subject]))
                )
                for subject in group_combo
            ):
                continue
            
            # Create merged schedule with new format
            schedule_subjects = {}
            for subject in group_combo:
                subgroup = int(subgroup_combo.get(subject, group_combo[subject]))
                schedule_subjects[subject] = {
                    "group": int(group_combo[subject]), 
                    "subgroup": subgroup
                }
                
            url = generate_url(schedule_subjects, quadrimester)
            schedule_entry = {
                "subjects": schedule_subjects,
                "url": url
            }
            
            schedules.append(schedule_entry)
            urls.append(url)

    # Stop progress thread if it was started
    if thread:
        progress["done"] = True
        thread.join()
    
    return schedules, urls


def split_schedule_by_group_type(parsed_schedule: Dict[str, Any]) -> Tuple[Dict[str, Dict[str, List[Dict[str, Any]]]], 
                                                                         Dict[str, Dict[str, List[Dict[str, Any]]]]]:
    """Split schedule into main groups and subgroups."""
    group_schedule = {}
    subgroup_schedule = {}
    
    # Separate main groups and subgroups
    for subject, groups in parsed_schedule.items():
        for group_id, classes in groups.items():
            if not group_id.isdigit():
                continue
                
            group_number = int(group_id)
            if group_number % 10 != 0:
                # This is a subgroup
                subgroup_schedule.setdefault(subject, {})[group_id] = classes
                
                # Include the matching main group
                main_group_id = str(group_number - (group_number % 10))
                if main_group_id in parsed_schedule[subject]:
                    group_schedule.setdefault(subject, {})[main_group_id] = parsed_schedule[subject][main_group_id]
            else:
                # This is a main group
                group_schedule.setdefault(subject, {})[group_id] = classes
                
    return group_schedule, subgroup_schedule


def get_schedule_combinations(
    quadrimester: str,
    subjects: List[str],
    start_hour: int,
    end_hour: int,
    languages: List[str],
    same_subgroup_as_group: bool,
    relax_days: int,
    blacklisted_groups: List[List[Any]],
    show_progress: bool = False,
) -> Dict[str, Any]:
    """Find all valid schedule combinations for the given subjects and constraints."""
    # Setup language
    language = "en"
    display_language = LANGUAGE_MAPPING.get(language, DEFAULT_LANGUAGE)
    allowed_languages = languages[:] + ["Per determinar"]
    max_days = 5 - relax_days
    
    # Save original end hour for response
    original_end_hour = end_hour
    
    # Adjust end hour (inclusive)
    end_hour -= 1
    
    # Ensure subjects are uppercase
    subjects = [subject.upper() for subject in subjects]
    blacklisted_groups = [[subject.upper(), group] for subject, group in blacklisted_groups]
    
    logger.debug(
        f"Parameters: quadrimester={quadrimester}, subjects={subjects}, hours={start_hour}-{end_hour}, "
        f"languages={languages}, same_subgroup={same_subgroup_as_group}, "
        f"max_days={max_days}, blacklist={blacklisted_groups}, language={display_language}"
    )

    # Fetch and parse class data
    raw_data = fetch_classes_data(quadrimester, display_language)
    parsed_schedule = parse_classes_data(raw_data)
    
    # Debug: show parsed subjects and group counts
    for subject, groups in parsed_schedule.items():
        logger.debug(f"  {subject}: {len(groups)} group entries")

    # Split schedule into main groups and subgroups
    group_schedule, subgroup_schedule = split_schedule_by_group_type(parsed_schedule)
    
    # Debug: show group counts for requested subjects
    for subject in subjects:
        logger.debug(f"Main groups for {subject}: {list(group_schedule.get(subject, {}).keys())}")
        logger.debug(f"Subgroups for {subject}: {list(subgroup_schedule.get(subject, {}).keys())}")

    # Get valid combinations
    valid_groups = get_valid_group_combinations(
        group_schedule, subjects, blacklisted_groups, allowed_languages, start_hour, end_hour
    )
    
    valid_subgroups = get_valid_subgroup_combinations(
        subgroup_schedule, subjects, blacklisted_groups, allowed_languages, start_hour, end_hour
    )

    # Merge valid schedules
    schedules, urls = merge_valid_schedules(
        valid_groups, valid_subgroups, group_schedule, subgroup_schedule,
        max_days, start_hour, end_hour, same_subgroup_as_group, quadrimester,
        show_progress
    )
    
    # Convert language codes to natural language
    natural_languages = []
    lang_map = {"en": "English", "es": "Spanish", "ca": "Catalan"}
    for lang in languages:
        natural_lang = lang_map.get(lang.lower(), lang)
        natural_languages.append(natural_lang)

    # Build result in the new format
    result = {
        "quad": quadrimester,
        "start": start_hour,
        "end": original_end_hour,
        "same_subgroup_as_group": same_subgroup_as_group,
        "languages": natural_languages,
        "subjects": subjects,
        "total": len(schedules),
        "schedules": schedules
    }
    
    logger.debug(f"Found {len(schedules)} valid schedules")
    return result