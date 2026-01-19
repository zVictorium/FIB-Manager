"""
Module for validating schedules and generating valid combinations.

Optimized version with:
- Precomputed slot sets for O(1) conflict detection
- Early pruning during combination generation
- Set-based operations for fast membership tests
- Lazy evaluation with generators
- Caching of computed values
"""

import itertools
import logging
import sys
import threading
from functools import lru_cache
from typing import Dict, List, Tuple, Set, Any, Iterator, FrozenSet, Optional

from app.api import generate_schedule_url
from app.core.utils import run_progress_thread, is_whitelist_satisfied

# Initialize module logger
logger = logging.getLogger(__name__)

# Type aliases for clarity
Slot = Tuple[int, int]  # (day, hour)
SlotSet = FrozenSet[Slot]

class SlotCache:
    """Cache for precomputed slot information to avoid redundant calculations.
    
    This dramatically improves performance by computing slot sets once per group
    instead of recomputing for every combination check.
    """
    
    def __init__(self):
        self._group_slots: Dict[Tuple[str, str], SlotSet] = {}
        self._group_hours: Dict[Tuple[str, str], FrozenSet[int]] = {}
        self._group_days: Dict[Tuple[str, str], FrozenSet[int]] = {}
        self._dead_hours_cache: Dict[SlotSet, int] = {}
    
    def precompute_slots(self, schedule: Dict[str, Any]) -> None:
        """Precompute all slot sets for a schedule."""
        for subject, groups in schedule.items():
            for group_id, classes in groups.items():
                if not isinstance(classes, list):
                    continue
                key = (subject, group_id)
                slots = frozenset((entry["day"], entry["hour"]) for entry in classes)
                hours = frozenset(entry["hour"] for entry in classes)
                days = frozenset(entry["day"] for entry in classes)
                self._group_slots[key] = slots
                self._group_hours[key] = hours
                self._group_days[key] = days
    
    def get_slots(self, subject: str, group: str) -> SlotSet:
        """Get cached slot set for a subject/group combination."""
        return self._group_slots.get((subject, group), frozenset())
    
    def get_hours(self, subject: str, group: str) -> FrozenSet[int]:
        """Get cached hours set for a subject/group combination."""
        return self._group_hours.get((subject, group), frozenset())
    
    def get_days(self, subject: str, group: str) -> FrozenSet[int]:
        """Get cached days set for a subject/group combination."""
        return self._group_days.get((subject, group), frozenset())
    
    def get_combo_slots(self, schedule: Dict[str, Any], combination: Dict[str, Any]) -> SlotSet:
        """Get combined slot set for a combination, using cache."""
        all_slots: Set[Slot] = set()
        for subject, group in combination.items():
            all_slots.update(self.get_slots(subject, str(group)))
        return frozenset(all_slots)
    
    def has_conflicts_fast(self, slots1: SlotSet, slots2: SlotSet) -> bool:
        """Fast conflict detection using set intersection."""
        return bool(slots1 & slots2)
    
    def get_dead_hours_cached(self, slots: SlotSet) -> int:
        """Calculate dead hours with caching."""
        if slots in self._dead_hours_cache:
            return self._dead_hours_cache[slots]
        
        dead_hours = _calculate_dead_hours_from_slots(slots)
        self._dead_hours_cache[slots] = dead_hours
        return dead_hours


# Global cache instance
_slot_cache = SlotCache()


def clear_cache() -> None:
    """Clear the global slot cache.
    
    Call this between independent schedule searches to free memory
    and avoid stale data issues.
    """
    global _slot_cache
    _slot_cache = SlotCache()


def _calculate_dead_hours_from_slots(slots: SlotSet) -> int:
    """Calculate dead hours from a frozenset of slots."""
    if not slots:
        return 0
    
    # Group by day
    days_hours: Dict[int, List[int]] = {}
    for day, hour in slots:
        days_hours.setdefault(day, []).append(hour)
    
    dead_hours = 0
    for day, hours in days_hours.items():
        if len(hours) < 2:
            continue
        hours_sorted = sorted(hours)
        span = hours_sorted[-1] - hours_sorted[0] + 1
        dead_hours += span - len(hours)
    
    return dead_hours


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
    
    Optimized version using set operations for faster computation.
    
    Args:
        slots: Dictionary mapping (day, hour) slots to lists of subjects
    
    Returns:
        Total number of dead hours across all days
    """
    if not slots:
        return 0
    
    # Group slots by day using a dict
    days_hours: Dict[int, List[int]] = {}
    for (day, hour), subjects in slots.items():
        if subjects:  # Only count hours with actual classes
            days_hours.setdefault(day, []).append(hour)
    
    dead_hours = 0
    for hours in days_hours.values():
        if len(hours) < 2:
            continue
        # Optimized: use min/max and set membership instead of sorting
        hours_set = set(hours)
        first_class = min(hours)
        last_class = max(hours)
        # Count gaps using range and set difference
        expected_count = last_class - first_class + 1
        dead_hours += expected_count - len(hours_set)
    
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
                      end_hour: int,
                      blacklist_set: Optional[FrozenSet[Tuple[str, int]]] = None) -> bool:
    """
    Check if a schedule is valid.
    
    Optimized version with:
    - Set-based blacklist checking
    - Early exit on any constraint violation
    - Reduced redundant computations
    
    Args:
        schedule: Dictionary containing parsed class data
        combination: Dictionary mapping subjects to groups
        blacklist: List of [subject, group] pairs
        allowed_languages: List of allowed languages
        start_hour: Minimum allowed hour
        end_hour: Maximum allowed hour
        blacklist_set: Pre-computed frozenset for faster blacklist checks
    
    Returns:
        True if the schedule is valid, False otherwise
    """
    # Use pre-computed blacklist set if available, otherwise compute
    if blacklist_set is None:
        blacklist_set = frozenset((item[0], int(item[1])) for item in blacklist)
    
    used_slots: Set[Tuple[int, int]] = set()
    min_hour = float('inf')
    max_hour = float('-inf')
    
    for subject, group in combination.items():
        group_int = int(group)
        # Fast blacklist check using set
        if (subject, group_int) in blacklist_set:
            return False
        
        entries = schedule.get(subject, {}).get(str(group), [])
        for entry in entries:
            # Early language check
            if allowed_languages:
                lang = entry.get("language", "")
                if lang and not any(al.lower() in lang.lower() for al in allowed_languages):
                    return False
            
            hour = entry["hour"]
            # Early time bounds check per entry
            if hour < start_hour or hour > end_hour:
                return False
            
            slot = (entry["day"], hour)
            # Fast conflict detection using set
            if slot in used_slots:
                return False
            used_slots.add(slot)
            
            # Track min/max for bounds check (optimized away since we check per entry)
            if hour < min_hour:
                min_hour = hour
            if hour > max_hour:
                max_hour = hour
    
    return True


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
    
    Optimized version with:
    - Pre-filtering of invalid groups before combination generation
    - Precomputed blacklist set for O(1) lookup
    - Reduced combination space through early constraint application
    
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
    # Precompute blacklist set for O(1) lookups
    blacklist_set = frozenset((item[0], int(item[1])) for item in blacklist)
    
    # Pre-filter valid groups per subject before generating combinations
    # This dramatically reduces the combination space
    valid_groups_per_subject: Dict[str, List[str]] = {}
    
    for subject in subjects:
        if subject not in schedule:
            continue
        
        valid_groups = []
        for group_id, classes in schedule[subject].items():
            if not isinstance(classes, list):
                continue
            
            # Skip blacklisted groups
            if (subject, int(group_id)) in blacklist_set:
                continue
            
            # Check if group passes basic constraints
            is_valid = True
            for entry in classes:
                hour = entry.get("hour", 0)
                # Time bounds check
                if hour < start_hour or hour > end_hour:
                    is_valid = False
                    break
                # Language check
                if allowed_languages:
                    lang = entry.get("language", "")
                    if lang and not any(al.lower() in lang.lower() for al in allowed_languages):
                        is_valid = False
                        break
            
            if is_valid:
                valid_groups.append(group_id)
        
        if valid_groups:
            valid_groups_per_subject[subject] = valid_groups
    
    # If any subject has no valid groups, return empty
    if len(valid_groups_per_subject) != len([s for s in subjects if s in schedule]):
        return []
    
    # Precompute slot cache for conflict detection
    _slot_cache.precompute_slots(schedule)
    
    # Generate combinations only from valid groups
    valid = []
    subjects_ordered = list(valid_groups_per_subject.keys())
    group_lists = [valid_groups_per_subject[s] for s in subjects_ordered]
    
    for combo_tuple in itertools.product(*group_lists):
        combo = dict(zip(subjects_ordered, combo_tuple))
        
        # Fast conflict check using precomputed slots
        all_slots: Set[Tuple[int, int]] = set()
        has_conflict = False
        
        for subject, group in combo.items():
            group_slots = _slot_cache.get_slots(subject, group)
            # Check for conflicts with already added slots
            if all_slots & group_slots:
                has_conflict = True
                break
            all_slots.update(group_slots)
        
        if not has_conflict:
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
                          whitelist: List[List[Any]] = None,
                          show_progress: bool = False
                          ) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Merge valid group and subgroup schedules.
    
    Optimized version with:
    - Precomputed slot sets for fast conflict detection
    - Early matching check before expensive slot computation
    - Cached slot sets avoid redundant computation
    - Fast set-based operations for conflict and day checks
    
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
        whitelist: List of [subject, group] pairs that must be included
        show_progress: Whether to show a progress bar
    
    Returns:
        Tuple of (merged_schedules, urls)
    """
    merged_schedules = []
    urls = []
    
    # Precompute slots for both schedules
    _slot_cache.precompute_slots(group_schedule)
    _slot_cache.precompute_slots(subgroup_schedule)
    
    # Precompute slot sets for all group combinations (avoid redundant computation)
    group_combo_slots: Dict[int, Tuple[SlotSet, FrozenSet[int]]] = {}
    for i, combo in enumerate(group_combos):
        slots: Set[Slot] = set()
        days: Set[int] = set()
        for subject, group in combo.items():
            group_slots = _slot_cache.get_slots(subject, group)
            group_days = _slot_cache.get_days(subject, group)
            slots.update(group_slots)
            days.update(group_days)
        group_combo_slots[i] = (frozenset(slots), frozenset(days))
    
    # Precompute slot sets for all subgroup combinations
    subgroup_combo_slots: Dict[int, Tuple[SlotSet, FrozenSet[int]]] = {}
    for i, combo in enumerate(subgroup_combos):
        slots: Set[Slot] = set()
        days: Set[int] = set()
        for subject, group in combo.items():
            sub_slots = _slot_cache.get_slots(subject, group)
            sub_days = _slot_cache.get_days(subject, group)
            slots.update(sub_slots)
            days.update(sub_days)
        subgroup_combo_slots[i] = (frozenset(slots), frozenset(days))
    
    # If require_matching, precompute matching map to avoid redundant checks
    matching_subgroups: Optional[Dict[int, List[int]]] = None
    if require_matching:
        matching_subgroups = {}
        for gi, group_combo in enumerate(group_combos):
            matching = []
            for si, subgroup_combo in enumerate(subgroup_combos):
                if are_groups_matching(group_combo, subgroup_combo):
                    matching.append(si)
            matching_subgroups[gi] = matching
    
    total_iters = max(len(group_combos) * len(subgroup_combos), 1)
    progress = {"count": 0, "total": total_iters, "done": False}
    thread = None
    if show_progress and sys.stdout.isatty():
        thread = threading.Thread(target=run_progress_thread, args=(progress,), daemon=True)
        thread.start()
    
    for gi, group_combo in enumerate(group_combos):
        g_slots, g_days = group_combo_slots[gi]
        
        # Determine which subgroups to check
        subgroup_indices = matching_subgroups[gi] if matching_subgroups else range(len(subgroup_combos))
        
        for si in subgroup_indices:
            progress["count"] += 1
            subgroup_combo = subgroup_combos[si]
            s_slots, s_days = subgroup_combo_slots[si]
            
            # Fast conflict check using set intersection
            if g_slots & s_slots:
                continue
            
            # Fast days check
            combined_days = g_days | s_days
            if len(combined_days) > max_days:
                continue
            
            # Check dead hours only if there's a limit
            if max_dead_hours >= 0:
                combined_slots = g_slots | s_slots
                dead_hours = _slot_cache.get_dead_hours_cached(combined_slots)
                if dead_hours > max_dead_hours:
                    continue
            
            # Create schedule entry before whitelist check
            subjects_entry = create_schedule_subjects(group_combo, subgroup_combo)
            
            # Check whitelist - schedule must include ALL whitelisted groups
            if whitelist and not is_whitelist_satisfied(subjects_entry, whitelist):
                continue
            
            # All checks passed - add schedule entry
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
