"""
Scheduler module that uses other modules to generate valid schedules.
"""

import logging
from typing import Dict, List, Any

from app.core.constants import LANGUAGE_MAPPING, DEFAULT_LANGUAGE
from app.api import fetch_classes_data
from app.core.parser import parse_classes_data, split_schedule_by_group_type
from app.core.utils import run_progress_thread
from app.core.validator import (
    get_valid_combinations,
    merge_valid_schedules
)

# Initialize module logger
logger = logging.getLogger(__name__)

# Debug flag
DEBUG = False

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
    """
    Get valid schedule combinations.
    
    Args:
        quadrimester: Quadrimester code
        subjects: List of subject codes
        start_hour: Minimum allowed hour
        end_hour: Maximum allowed hour
        languages: List of allowed languages
        require_matching_subgroup: Whether to require matching groups and subgroups
        relax_days: Number of days to relax the schedule by
        blacklist: List of [subject, group] pairs
        show_progress: Whether to show a progress bar
    
    Returns:
        Dictionary containing the schedule combinations
    """
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
    
    schedules, urls = merge_valid_schedules(
        valid_group_combos, valid_subgroup_combos,
        group_schedule, subgroup_schedule,
        max_days, start_hour, end_hour,
        require_matching_subgroup, quadrimester,
        show_progress
    )
    
    natural_languages = [{"en": "English", "es": "Spanish", "ca": "Catalan"}.get(lang.lower(), lang)
                         for lang in languages]
    
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
