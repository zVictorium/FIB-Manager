import requests
import itertools
import logging
import os
import shutil
import threading
import time
import sys
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


# -------------------------
# API and Data Fetch Helpers
# -------------------------
def get_json_response(url: str, language: str) -> Dict[str, Any]:
    headers = {"Accept-Language": language}
    logger.debug("Requesting data: %s", url)
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logger.error("Failed to fetch data: HTTP %s", response.status_code)
        return {"results": []}
    return response.json()


def get_paginated_data(base_url: str, language: str) -> List[Dict[str, Any]]:
    results = []
    current_url = base_url
    while current_url:
        page = get_json_response(current_url, language)
        results.extend(page.get("results", []))
        current_url = page.get("next")  # will be None or empty when finished
    return results


def fetch_classes_data(quadrimester: str, language: str) -> Dict[str, List[Dict[str, Any]]]:
    url = f"{API_BASE_URL}/quadrimestres/{quadrimester}/classes.json?client_id={CLIENT_ID}&lang={language}"
    data = get_paginated_data(url, language)
    logger.debug("Fetched %d class entries", len(data))
    return {"results": data}


def fetch_subject_names(language: str) -> Dict[str, str]:
    url = f"{API_BASE_URL}/assignatures.json?format=json&client_id={CLIENT_ID}&lang={language}"
    subjects = get_paginated_data(url, language)
    names = {item.get("id"): item.get("nom") for item in subjects if item.get("id") and item.get("nom")}
    logger.debug("Fetched %d subjects", len(names))
    return names


# -------------------------
# Data Parsing and Transformation
# -------------------------
def extract_class_info(class_entry: Dict[str, Any]) -> List[Dict[str, Any]]:
    time_str = class_entry.get("inici", "00:00")
    time_parts = time_str.split(":")
    if len(time_parts) < 2:
        return []
    start_hour = int(time_parts[0])
    duration = int(class_entry.get("durada", 0))
    base_info = {
        "type": class_entry.get("tipus", ""),
        "classroom": class_entry.get("aules", []),
        "language": class_entry.get("idioma", ""),
        "day": class_entry.get("dia_setmana", 0),
        "group": int(class_entry.get("grup", 0)),
    }
    return [dict(base_info, hour=start_hour + offset) for offset in range(duration)]


def is_valid_class_entry(class_entry: Dict[str, Any]) -> bool:
    if not class_entry.get("codi_assig") or not class_entry.get("grup"):
        return False
    try:
        int(class_entry.get("grup"))
    except ValueError:
        return False
    return True


def parse_classes_data(data: Dict[str, Any]) -> Dict[str, Any]:
    schedule = {}
    for entry in data.get("results", []):
        if not is_valid_class_entry(entry):
            continue
        subject = entry.get("codi_assig")
        group_key = str(entry.get("grup"))
        class_entries = extract_class_info(entry)
        if not class_entries:
            continue
        subject_info = schedule.setdefault(subject, {"name": subject})
        subject_info.setdefault(group_key, []).extend(class_entries)
    add_missing_groups(schedule)
    return schedule


def add_missing_groups(schedule: Dict[str, Any]) -> None:
    # Add missing subgroup for each main group (tens)
    for subject, groups in schedule.items():
        main_groups = [grp for grp in groups if grp.isdigit() and int(grp) % 10 == 0]
        for mg in main_groups:
            groups.setdefault(str(int(mg) + 1), [])
    # Ensure main group exists if subgroup is present
    for subject, groups in schedule.items():
        for grp in list(groups.keys()):
            if grp.isdigit() and int(grp) % 10 != 0:
                main_grp = str(int(grp) - (int(grp) % 10))
                groups.setdefault(main_grp, [])


def split_schedule_by_group_type(parsed_schedule: Dict[str, Any]
                                ) -> Tuple[Dict[str, Dict[str, List[Dict[str, Any]]]], 
                                           Dict[str, Dict[str, List[Dict[str, Any]]]]]:
    group_schedule = {}
    subgroup_schedule = {}
    for subject, groups in parsed_schedule.items():
        for group_id, classes in groups.items():
            if not group_id.isdigit():
                continue
            group_number = int(group_id)
            if group_number % 10 == 0:
                group_schedule.setdefault(subject, {})[group_id] = classes
            else:
                subgroup_schedule.setdefault(subject, {})[group_id] = classes
                main_group_id = str(group_number - (group_number % 10))
                if main_group_id in parsed_schedule[subject]:
                    group_schedule.setdefault(subject, {})[main_group_id] = parsed_schedule[subject][main_group_id]
    return group_schedule, subgroup_schedule


# -------------------------
# Schedule Validation Helpers
# -------------------------
def get_time_slots(schedule: Dict[str, Any], combination: Dict[str, Any]) -> Dict[Tuple[int, int], List[str]]:
    slots = {}
    for subject, group in combination.items():
        for entry in schedule.get(subject, {}).get(str(group), []):
            slot = (entry["day"], entry["hour"])
            slots.setdefault(slot, []).append(subject)
    return slots


def get_days_with_classes(slots: Dict[Tuple[int, int], List[str]]) -> Set[int]:
    return {day for day, _ in slots.keys()}


def is_within_time_bounds(hours: Set[int], start_hour: int, end_hour: int) -> bool:
    if not hours:
        return True
    return min(hours) >= start_hour and max(hours) <= end_hour


def is_language_compatible(class_language: str, allowed_languages: List[str]) -> bool:
    if not class_language or not allowed_languages:
        return True
    class_language = class_language.lower()
    return any(lang.lower() in class_language for lang in allowed_languages)


def is_group_blacklisted(subject: str, group: str, blacklist: List[List[Any]]) -> bool:
    return [subject, int(group)] in blacklist


def is_valid_schedule(schedule: Dict[str, Any],
                      combination: Dict[str, Any],
                      blacklist: List[List[Any]],
                      allowed_languages: List[str],
                      start_hour: int,
                      end_hour: int) -> bool:
    used_slots = {}
    hours_set = set()
    for subject, group in combination.items():
        if is_group_blacklisted(subject, group, blacklist):
            return False
        for entry in schedule.get(subject, {}).get(str(group), []):
            if not is_language_compatible(entry.get("language", ""), allowed_languages):
                return False
            slot = (entry["day"], entry["hour"])
            if slot in used_slots:
                return False
            used_slots[slot] = True
            hours_set.add(entry["hour"])
    return is_within_time_bounds(hours_set, start_hour, end_hour)


def has_schedule_conflicts(slots: Dict[Tuple[int, int], List[str]]) -> bool:
    return any(len(subjects) > 1 for subjects in slots.values())


def count_days_with_classes(group_slots: Dict[Tuple[int, int], List[str]],
                            subgroup_slots: Dict[Tuple[int, int], List[str]]) -> int:
    days = get_days_with_classes(group_slots)
    days.update(get_days_with_classes(subgroup_slots))
    return len(days)


def has_valid_combined_schedule(group_slots: Dict[Tuple[int, int], List[str]],
                                subgroup_slots: Dict[Tuple[int, int], List[str]],
                                max_days: int,
                                start_hour: int,
                                end_hour: int) -> bool:
    # Merge slots from both groups
    all_slots = {slot: subjects[:] for slot, subjects in group_slots.items()}
    for slot, subjects in subgroup_slots.items():
        all_slots.setdefault(slot, []).extend(subjects)
    if has_schedule_conflicts(all_slots):
        return False
    if count_days_with_classes(group_slots, subgroup_slots) > max_days:
        return False
    hours = {hour for _, hour in all_slots.keys()} if all_slots else set()
    return is_within_time_bounds(hours, start_hour, end_hour)


def are_groups_matching(group_combo: Dict[str, str], subgroup_combo: Dict[str, str]) -> bool:
    return all(
        (int(group_combo[subject]) // 10) == (int(subgroup_combo.get(subject, group_combo[subject])) // 10)
        for subject in group_combo
    )


def create_schedule_subjects(group_combo: Dict[str, str],
                             subgroup_combo: Dict[str, str]) -> Dict[str, Dict[str, int]]:
    result = {}
    for subject in group_combo:
        result[subject] = {
            "group": int(group_combo[subject]),
            "subgroup": int(subgroup_combo.get(subject, group_combo[subject])),
        }
    return result


# -------------------------
# Progress Display (for Terminal)
# -------------------------
def update_terminal_progress(count: int, total: int) -> None:
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
    count_text = Text(f"{count}/{total}", style=FILLED_BAR_COLOR)

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
    if not sys.stdout.isatty():
        return
    last = -1
    while not progress["done"]:
        if progress["count"] != last:
            update_terminal_progress(progress["count"], progress["total"])
            last = progress["count"]
        time.sleep(0.1)
    update_terminal_progress(progress["total"], progress["total"])


# -------------------------
# Valid Combinations and Merging Schedules
# -------------------------
def get_valid_combinations(schedule: Dict[str, Dict[str, List[Dict[str, Any]]]],
                           subjects: List[str],
                           blacklist: List[List[Any]],
                           allowed_languages: List[str],
                           start_hour: int,
                           end_hour: int) -> List[Dict[str, str]]:
    available = {s: list(schedule[s].keys()) for s in subjects if s in schedule}
    logger.debug("Available groups for subjects: %s", available)
    all_combos = [dict(zip(available.keys(), combo)) for combo in itertools.product(*available.values())]
    valid = []
    for combo in all_combos:
        if is_valid_schedule(schedule, combo, blacklist, allowed_languages, start_hour, end_hour):
            valid.append(combo)
    logger.debug("Valid combinations count: %d", len(valid))
    return valid


def merge_valid_schedules(group_combos: List[Dict[str, str]],
                          subgroup_combos: List[Dict[str, str]],
                          group_schedule: Dict[str, Dict[str, List[Dict[str, Any]]]],
                          subgroup_schedule: Dict[str, Dict[str, List[Dict[str, Any]]]],
                          max_days: int,
                          start_hour: int,
                          end_hour: int,
                          require_matching: bool,
                          quadrimester: str,
                          show_progress: bool = False
                          ) -> Tuple[List[Dict[str, Any]], List[str]]:
    merged_schedules = []
    urls = []
    total_iters = max(len(group_combos) * len(subgroup_combos), 1)
    progress = {"count": 0, "total": total_iters, "done": False}
    thread = None
    if show_progress and sys.stdout.isatty():
        thread = threading.Thread(target=run_progress_thread, args=(progress,), daemon=True)
        thread.start()

    for group_combo in group_combos:
        for subgroup_combo in subgroup_combos:
            progress["count"] += 1
            group_slots = get_time_slots(group_schedule, group_combo)
            subgroup_slots = get_time_slots(subgroup_schedule, subgroup_combo)
            if not has_valid_combined_schedule(group_slots, subgroup_slots, max_days, start_hour, end_hour):
                continue
            if require_matching and not are_groups_matching(group_combo, subgroup_combo):
                continue
            subjects_entry = create_schedule_subjects(group_combo, subgroup_combo)
            url = generate_schedule_url(subjects_entry, quadrimester)
            merged_schedules.append({"subjects": subjects_entry, "url": url})
            urls.append(url)
    if thread:
        progress["done"] = True
        thread.join()
    return merged_schedules, urls


def generate_schedule_url(schedule_subjects: Dict[str, Dict[str, int]], quadrimester: str) -> str:
    base_url = "https://www.fib.upc.edu/en/studies/bachelors-degrees/bachelor-degree-informatics-engineering/timetables"
    params = f"?&class=true&lang=true&quad={quadrimester}"
    parts = []
    for subject, grp_info in schedule_subjects.items():
        parts.append(f"a={subject}_{grp_info['group']}")
        parts.append(f"a={subject}_{grp_info['subgroup']}")
    return base_url + params + "&" + "&".join(parts)


# -------------------------
# Main Combination Generator
# -------------------------
def get_schedule_combinations(
    quadrimester: str,
    subjects: List[str],
    start_hour: int,
    end_hour: int,
    languages: List[str],
    require_matching_subgroup: bool,
    relax_days: int,
    blacklist: List[List[Any]],
    show_progress: bool = False,
) -> Dict[str, Any]:
    language = "en"
    display_language = LANGUAGE_MAPPING.get(language, DEFAULT_LANGUAGE)
    allowed_languages = languages + ["Per determinar"]
    max_days = 5 - relax_days
    original_end_hour = end_hour
    end_hour -= 1  # adjust inclusive

    logger.debug(
        "Params: quad=%s, subjects=%s, hours=%d-%d, langs=%s, require_matching=%s, max_days=%d, blacklist=%s, lang_disp=%s",
        quadrimester, subjects, start_hour, end_hour, languages, require_matching_subgroup, max_days, blacklist, display_language
    )
    raw_data = fetch_classes_data(quadrimester, display_language)
    parsed_schedule = parse_classes_data(raw_data)
    group_schedule, subgroup_schedule = split_schedule_by_group_type(parsed_schedule)
    for subject in subjects:
        logger.debug("Subject %s main groups: %s; subgroups: %s",
                     subject,
                     list(group_schedule.get(subject, {}).keys()),
                     list(subgroup_schedule.get(subject, {}).keys()))
    valid_group_combos = get_valid_combinations(group_schedule, subjects, blacklist, allowed_languages, start_hour, end_hour)
    valid_subgroup_combos = get_valid_combinations(subgroup_schedule, subjects, blacklist, allowed_languages, start_hour, end_hour)
    schedules, urls = merge_valid_schedules(valid_group_combos, valid_subgroup_combos,
                                             group_schedule, subgroup_schedule,
                                             max_days, start_hour, end_hour,
                                             require_matching_subgroup, quadrimester,
                                             show_progress)
    natural_languages = [ {"en": "English", "es": "Spanish", "ca": "Catalan"}.get(lang.lower(), lang)
                         for lang in languages ]
    result = {
        "quad": quadrimester,
        "start": start_hour,
        "end": original_end_hour,
        "same_subgroup_as_group": require_matching_subgroup,
        "languages": natural_languages,
        "subjects": subjects,
        "total": len(schedules),
        "schedules": schedules
    }
    logger.debug("Found %d valid schedules", len(schedules))
    return result