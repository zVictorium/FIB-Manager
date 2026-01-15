"""
Module for parsing and processing class data.
"""

from typing import Dict, List, Tuple, Any

def extract_class_info(class_entry: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract class information from a class entry.
    
    Args:
        class_entry: Class entry from the API
    
    Returns:
        List of dictionaries with class information
    """
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
    """
    Check if a class entry is valid.
    
    Args:
        class_entry: Class entry from the API
    
    Returns:
        True if the entry is valid, False otherwise
    """
    if not class_entry.get("codi_assig") or not class_entry.get("grup"):
        return False
    try:
        int(class_entry.get("grup"))
    except ValueError:
        return False
    return True


def parse_classes_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse class data from the API.
    
    Args:
        data: Class data from the API
    
    Returns:
        Dictionary containing parsed class data
    """
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
    """
    Add missing groups and subgroups to the schedule.
    
    Args:
        schedule: Dictionary containing parsed class data
    """
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
    """
    Split the schedule into group and subgroup schedules.
    
    Args:
        parsed_schedule: Dictionary containing parsed class data
    
    Returns:
        Tuple of (group_schedule, subgroup_schedule)
    """
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
