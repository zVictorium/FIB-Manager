"""
Module for validating schedules and generating valid combinations.
"""

import itertools
import logging
import sys
import threading
from typing import Dict, List, Tuple, Set, Any

from app.api import generate_schedule_url
from app.core.utils import run_progress_thread

# Initialize module logger
logger = logging.getLogger(__name__)

def get_time_slots(schedule: Dict[str, Any], combination: Dict[str, Any]) -> Dict[Tuple[int, int], List[str]]:
    """
    Get the time slots used by a schedule combination.
    
    Args:
        schedule: Dictionary containing parsed class data
        combination: Dictionary mapping subjects to groups
    
    Returns:
        Dictionary mapping (day, hour) slots to lists of subjects
    """
    slots = {}
    for subject, group in combination.items():
        for entry in schedule.get(subject, {}).get(str(group), []):
            slot = (entry["day"], entry["hour"])
            slots.setdefault(slot, []).append(subject)
    return slots


def get_days_with_classes(slots: Dict[Tuple[int, int], List[str]]) -> Set[int]:
    """
    Get the days with classes in a schedule.
    
    Args:
        slots: Dictionary mapping (day, hour) slots to lists of subjects
    
    Returns:
        Set of days with classes
    """
    return {day for day, _ in slots.keys()}


def count_dead_hours(slots: Dict[Tuple[int, int], List[str]]) -> int:
    """
    Count the number of dead hours in a schedule.
    A dead hour is an hour without classes between two hours with classes on the same day.
    
    Args:
        slots: Dictionary mapping (day, hour) slots to lists of subjects
    
    Returns:
        Total number of dead hours across all days
    """
    dead_hours = 0
    
    # Group slots by day
    days_schedule = {}
    for (day, hour), subjects in slots.items():
        if subjects:  # Only count hours with actual classes
            days_schedule.setdefault(day, []).append(hour)
    
    # For each day, count dead hours between first and last class
    for day, hours in days_schedule.items():
        if len(hours) < 2:  # Need at least 2 classes to have dead hours
            continue
            
        hours.sort()  # Ensure hours are in order
        first_class = min(hours)
        last_class = max(hours)
        
        # Count hours between first and last that don't have classes
        for hour in range(first_class + 1, last_class):
            if hour not in hours:
                dead_hours += 1
    
    return dead_hours


def is_within_time_bounds(hours: Set[int], start_hour: int, end_hour: int) -> bool:
    """
    Check if a schedule is within the specified time bounds.
    
    Args:
        hours: Set of hours with classes
        start_hour: Minimum allowed hour
        end_hour: Maximum allowed hour
    
    Returns:
        True if the schedule is within the time bounds, False otherwise
    """
    if not hours:
        return True
    return min(hours) >= start_hour and max(hours) <= end_hour


def is_language_compatible(class_language: str, allowed_languages: List[str]) -> bool:
    """
    Check if a class language is compatible with the allowed languages.
    
    Args:
        class_language: Class language
        allowed_languages: List of allowed languages
    
    Returns:
        True if the class language is compatible, False otherwise
    """
    if not class_language or not allowed_languages:
        return True
    class_language = class_language.lower()
    return any(lang.lower() in class_language for lang in allowed_languages)


def is_group_blacklisted(subject: str, group: str, blacklist: List[List[Any]]) -> bool:
    """
    Check if a group is blacklisted.
    
    Args:
        subject: Subject code
        group: Group number
        blacklist: List of [subject, group] pairs
    
    Returns:
        True if the group is blacklisted, False otherwise
    """
    return [subject, int(group)] in blacklist


def is_valid_schedule(schedule: Dict[str, Any],
                      combination: Dict[str, Any],
                      blacklist: List[List[Any]],
                      allowed_languages: List[str],
                      start_hour: int,
                      end_hour: int) -> bool:
    """
    Check if a schedule is valid.
    
    Args:
        schedule: Dictionary containing parsed class data
        combination: Dictionary mapping subjects to groups
        blacklist: List of [subject, group] pairs
        allowed_languages: List of allowed languages
        start_hour: Minimum allowed hour
        end_hour: Maximum allowed hour
    
    Returns:
        True if the schedule is valid, False otherwise
    """
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
    """
    Check if a schedule has conflicts.
    
    Args:
        slots: Dictionary mapping (day, hour) slots to lists of subjects
    
    Returns:
        True if the schedule has conflicts, False otherwise
    """
    return any(len(subjects) > 1 for subjects in slots.values())


def count_days_with_classes(group_slots: Dict[Tuple[int, int], List[str]],
                            subgroup_slots: Dict[Tuple[int, int], List[str]]) -> int:
    """
    Count the number of days with classes in a schedule.
    
    Args:
        group_slots: Dictionary mapping (day, hour) slots to lists of subjects for groups
        subgroup_slots: Dictionary mapping (day, hour) slots to lists of subjects for subgroups
    
    Returns:
        Number of days with classes
    """
    days = get_days_with_classes(group_slots)
    days.update(get_days_with_classes(subgroup_slots))
    return len(days)


def has_valid_combined_schedule(group_slots: Dict[Tuple[int, int], List[str]],
                                subgroup_slots: Dict[Tuple[int, int], List[str]],
                                max_days: int,
                                start_hour: int,
                                end_hour: int,
                                max_dead_hours: int = -1) -> bool:
    """
    Check if a combined schedule is valid.
    
    Args:
        group_slots: Dictionary mapping (day, hour) slots to lists of subjects for groups
        subgroup_slots: Dictionary mapping (day, hour) slots to lists of subjects for subgroups
        max_days: Maximum allowed days with classes
        start_hour: Minimum allowed hour
        end_hour: Maximum allowed hour
        max_dead_hours: Maximum allowed dead hours (-1 for no limit)
    
    Returns:
        True if the combined schedule is valid, False otherwise
    """
    # Merge slots from both groups
    all_slots = {slot: subjects[:] for slot, subjects in group_slots.items()}
    for slot, subjects in subgroup_slots.items():
        all_slots.setdefault(slot, []).extend(subjects)
    if has_schedule_conflicts(all_slots):
        return False
    if count_days_with_classes(group_slots, subgroup_slots) > max_days:
        return False
    if has_excessive_dead_hours(group_slots, subgroup_slots, max_dead_hours):
        return False
    hours = {hour for _, hour in all_slots.keys()} if all_slots else set()
    return is_within_time_bounds(hours, start_hour, end_hour)


def are_groups_matching(group_combo: Dict[str, str], subgroup_combo: Dict[str, str]) -> bool:
    """
    Check if group and subgroup combinations match.
    
    Args:
        group_combo: Dictionary mapping subjects to groups
        subgroup_combo: Dictionary mapping subjects to subgroups
    
    Returns:
        True if the combinations match, False otherwise
    """
    return all(
        (int(group_combo[subject]) // 10) == (int(subgroup_combo.get(subject, group_combo[subject])) // 10)
        for subject in group_combo
    )


def create_schedule_subjects(group_combo: Dict[str, str],
                             subgroup_combo: Dict[str, str]) -> Dict[str, Dict[str, int]]:
    """
    Create a dictionary of subjects with groups and subgroups.
    
    Args:
        group_combo: Dictionary mapping subjects to groups
        subgroup_combo: Dictionary mapping subjects to subgroups
    
    Returns:
        Dictionary mapping subjects to dictionaries with group and subgroup information
    """
    result = {}
    for subject in group_combo:
        result[subject] = {
            "group": int(group_combo[subject]),
            "subgroup": int(subgroup_combo.get(subject, group_combo[subject])),
        }
    return result


def get_valid_combinations(schedule: Dict[str, Dict[str, List[Dict[str, Any]]]],
                           subjects: List[str],
                           blacklist: List[List[Any]],
                           allowed_languages: List[str],
                           start_hour: int,
                           end_hour: int) -> List[Dict[str, str]]:
    """
    Get valid schedule combinations.
    
    Args:
        schedule: Dictionary containing parsed class data
        subjects: List of subject codes
        blacklist: List of [subject, group] pairs
        allowed_languages: List of allowed languages
        start_hour: Minimum allowed hour
        end_hour: Maximum allowed hour
    
    Returns:
        List of valid schedule combinations
    """
    available = {s: list(schedule[s].keys()) for s in subjects if s in schedule}
    all_combos = [dict(zip(available.keys(), combo)) for combo in itertools.product(*available.values())]
    valid = []
    for combo in all_combos:
        if is_valid_schedule(schedule, combo, blacklist, allowed_languages, start_hour, end_hour):
            valid.append(combo)
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
                          max_dead_hours: int = -1,
                          show_progress: bool = False
                          ) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Merge valid group and subgroup schedules.
    
    Args:
        group_combos: List of valid group combinations
        subgroup_combos: List of valid subgroup combinations
        group_schedule: Dictionary containing parsed class data for groups
        subgroup_schedule: Dictionary containing parsed class data for subgroups
        max_days: Maximum allowed days with classes
        start_hour: Minimum allowed hour
        end_hour: Maximum allowed hour
        require_matching: Whether to require matching groups and subgroups
        quadrimester: Quadrimester code
        max_dead_hours: Maximum allowed dead hours (-1 for no limit)
        show_progress: Whether to show a progress bar
    
    Returns:
        Tuple of (merged_schedules, urls)
    """
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
            if not has_valid_combined_schedule(group_slots, subgroup_slots, max_days, start_hour, end_hour, max_dead_hours):
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


def has_excessive_dead_hours(group_slots: Dict[Tuple[int, int], List[str]],
                             subgroup_slots: Dict[Tuple[int, int], List[str]],
                             max_dead_hours: int) -> bool:
    """
    Check if a combined schedule has excessive dead hours.
    
    Args:
        group_slots: Dictionary mapping (day, hour) slots to lists of subjects for groups
        subgroup_slots: Dictionary mapping (day, hour) slots to lists of subjects for subgroups
        max_dead_hours: Maximum allowed dead hours (-1 for no limit)
    
    Returns:
        True if the schedule has excessive dead hours, False otherwise
    """
    if max_dead_hours < 0:  # No limit
        return False
    
    # Merge slots from both groups
    all_slots = {slot: subjects[:] for slot, subjects in group_slots.items()}
    for slot, subjects in subgroup_slots.items():
        all_slots.setdefault(slot, []).extend(subjects)
    
    # Count dead hours in the combined schedule
    dead_hours = count_dead_hours(all_slots)
    return dead_hours > max_dead_hours


def calculate_schedule_dead_hours(schedule_subjects: Dict[str, Dict[str, int]],
                                  group_schedule: Dict[str, Dict[str, List[Dict[str, Any]]]],
                                  subgroup_schedule: Dict[str, Dict[str, List[Dict[str, Any]]]]) -> int:
    """
    Calculate the total dead hours for a specific schedule.
    
    Args:
        schedule_subjects: Dictionary mapping subject codes to group information
        group_schedule: Dictionary containing parsed class data for groups
        subgroup_schedule: Dictionary containing parsed class data for subgroups
    
    Returns:
        Total number of dead hours in the schedule
    """
    all_slots = {}
    
    # Add group slots
    for subject, info in schedule_subjects.items():
        group = str(info.get("group", ""))
        if group and subject in group_schedule and group in group_schedule[subject]:
            for entry in group_schedule[subject][group]:
                slot = (entry["day"], entry["hour"])
                all_slots.setdefault(slot, []).append(subject)
    
    # Add subgroup slots
    for subject, info in schedule_subjects.items():
        subgroup = str(info.get("subgroup", ""))
        if subgroup and subject in subgroup_schedule and subgroup in subgroup_schedule[subject]:
            for entry in subgroup_schedule[subject][subgroup]:
                slot = (entry["day"], entry["hour"])
                all_slots.setdefault(slot, []).append(subject)
    
    return count_dead_hours(all_slots)


def calculate_schedule_group_sum(schedule_subjects: Dict[str, Dict[str, int]]) -> int:
    """
    Calculate the sum of all group numbers in a schedule.
    
    Args:
        schedule_subjects: Dictionary mapping subject codes to group information
    
    Returns:
        Sum of all group numbers (lower sums indicate lower-numbered groups)
    """
    total_sum = 0
    for subject, info in schedule_subjects.items():
        if info.get("group"):
            total_sum += info["group"]
        if info.get("subgroup"):
            total_sum += info["subgroup"]
    return total_sum


def sort_schedules_by_mode(schedules: List[Dict[str, Any]], 
                          sort_mode: str,
                          group_schedule: Dict[str, Dict[str, List[Dict[str, Any]]]] = None,
                          subgroup_schedule: Dict[str, Dict[str, List[Dict[str, Any]]]] = None) -> List[Dict[str, Any]]:
    """
    Sort schedules based on the specified mode.
    
    Args:
        schedules: List of schedules to sort
        sort_mode: Sorting mode - "groups" or "dead_hours"
        group_schedule: Dictionary containing parsed class data for groups (required for dead_hours sort)
        subgroup_schedule: Dictionary containing parsed class data for subgroups (required for dead_hours sort)
    
    Returns:
        Sorted list of schedules
    """
    if sort_mode == "dead_hours":
        if not group_schedule or not subgroup_schedule:
            return schedules  # Can't sort without schedule data
          # Calculate dead hours for each schedule and add to schedule data
        for schedule in schedules:
            dead_hours = calculate_schedule_dead_hours(
                schedule.get("subjects", {}), group_schedule, subgroup_schedule
            )
            schedule["dead_hours"] = dead_hours
        
        # Sort by dead hours (ascending - fewer dead hours first)
        return sorted(schedules, key=lambda x: x.get("dead_hours", 0))
    
    elif sort_mode == "groups":
        # Calculate group sum for each schedule and add to schedule data
        for schedule in schedules:
            group_sum = calculate_schedule_group_sum(schedule.get("subjects", {}))
            schedule["group_sum"] = group_sum
        
        # Sort by group sum (ascending - lower group numbers first)
        return sorted(schedules, key=lambda x: x.get("group_sum", 0))
    
    return schedules
