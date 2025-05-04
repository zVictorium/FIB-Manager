import requests
import itertools
import logging
from typing import Any, Dict, List, Tuple

# Initialize module logger
logger = logging.getLogger(__name__)

API_BASE_URL: str = "https://api.fib.upc.edu/v2"
CLIENT_ID: str = "77qvbbQqni4TcEUsWvUCKOG1XU7Hr0EfIs4pacRz"
LANGUAGE_MAPPING: Dict[str, str] = {"en": "en", "es": "es", "ca": "ca", "": "ca"}


def fetch_classes_data_with_language(quad: str, language: str) -> Dict[str, List[Dict[str, Any]]]:
    """Fetch all class entries for a quadrimester, following pagination."""
    headers = {"Accept-Language": language}
    url = f"{API_BASE_URL}/quadrimestres/{quad}/classes.json?client_id={CLIENT_ID}&lang={language}"
    results: List[Dict[str, Any]] = []
    while url:
        logger.debug("Requesting classes data: %s", url)
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            logger.error("Failed to fetch classes data: HTTP %s", resp.status_code)
            break
        page = resp.json()
        results.extend(page.get("results", []))
        url = page.get("next") or ""
    logger.debug("Total class entries fetched: %d", len(results))
    return {"results": results}


def fetch_subject_names(language: str) -> Dict[str, str]:
    """Fetch code-to-name map for subjects, respecting pagination."""
    headers = {"Accept-Language": language}
    url = f"{API_BASE_URL}/assignatures.json?format=json&client_id={CLIENT_ID}&lang={language}"
    names: Dict[str, str] = {}
    while url:
        logger.debug("Requesting subject list: %s", url)
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            logger.error("Failed to fetch subjects data: HTTP %s", resp.status_code)
            break
        page = resp.json()
        for item in page.get("results", []):
            code = item.get("id")
            name = item.get("nom")
            if code and name:
                names[code] = name
        url = page.get("next") or ""
    logger.debug("Total subjects fetched: %d", len(names))
    return names


def parse_classes_data(data: Dict[str, Any]) -> Dict[str, Any]:
    parsed = {}
    for class_info in data.get("results", []):
        subj = class_info.get("codi_assig")
        grp = class_info.get("grup")
        if subj is None or grp is None:
            continue
        try:
            g = int(grp)
        except ValueError:
            continue
        time_parts = class_info.get("inici", "00:00").split(":")
        if len(time_parts) < 2:
            continue
        start_hour = int(time_parts[0])
        duration = class_info.get("durada", 0)
        parsed.setdefault(subj, {"name": subj})
        key = str(g)
        parsed[subj].setdefault(key, [])
        base = {
            "type": class_info.get("tipus", ""),
            "classroom": class_info.get("aules", []),
            "language": class_info.get("idioma", ""),
            "day": class_info.get("dia_setmana", 0),
            "group": g,
        }
        for offset in range(duration):
            entry = base.copy()
            entry["hour"] = start_hour + offset
            parsed[subj][key].append(entry)
    # Add missing subgroup for each main group
    for subj, groups in parsed.items():
        mains = [g for g in groups.keys() if g.isdigit() and int(g) % 10 == 0]
        for mg in mains:
            sg = str(int(mg) + 1)
            groups.setdefault(sg, [])
    # Add missing main group if subgroup exists
    for subj, groups in parsed.items():
        subs = [int(g) for g in groups.keys() if g.isdigit() and int(g) % 10 != 0]
        for sg in subs:
            mg = str(sg - (sg % 10))
            groups.setdefault(mg, [])
    return parsed


def get_time_slots(schedule: Dict[str, Any], combo: Dict[str, Any]) -> Dict[Tuple[int, int], List[str]]:
    slots = {}
    for subj, grp in combo.items():
        classes = schedule.get(subj, {}).get(str(grp), [])
        for ci in classes:
            slot = (ci["day"], ci["hour"])
            slots.setdefault(slot, []).append(subj)
    return slots


def count_total_days_with_classes(group_slots: Dict[Tuple[int, int], List[str]], subgroup_slots: Dict[Tuple[int, int], List[str]]) -> int:
    days = set()
    for day, _ in group_slots.keys():
        days.add(day)
    for day, _ in subgroup_slots.keys():
        days.add(day)
    return len(days)


def is_valid_schedule(schedule: Dict[str, Any], combo: Dict[str, Any], blacklisted: List[List[Any]], languages: List[str], start_hour: int, end_hour: int) -> bool:
    used_slots = {}
    hours = set()
    for subj, grp in combo.items():
        if [subj, int(grp)] in blacklisted:
            return False
        for ci in schedule.get(subj, {}).get(str(grp), []):
            # case-insensitive language check
            lang_field = ci.get("language", "").lower()
            lang_ok = False
            if not lang_field or not languages:
                lang_ok = True
            else:
                for lg in languages:
                    if lg.lower() in lang_field:
                        lang_ok = True
                        break
            if not lang_ok:
                return False
            slot = (ci["day"], ci["hour"])
            if slot in used_slots:
                return False
            used_slots[slot] = True
            hours.add(ci["hour"])
    if hours:
        if min(hours) < start_hour or max(hours) > end_hour:
            return False
    return True


def has_valid_schedule(group_slots: Dict[Tuple[int, int], List[str]], subgroup_slots: Dict[Tuple[int, int], List[str]], relax_days: int, start_hour: int, end_hour: int) -> bool:
    all_slots = {**{slot: subjects[:] for slot, subjects in group_slots.items()}}
    for slot, subs in subgroup_slots.items():
        all_slots.setdefault(slot, []).extend(subs)
    # conflict check
    for subs in all_slots.values():
        if len(subs) > 1:
            return False
    # day constraint
    days = count_total_days_with_classes(group_slots, subgroup_slots)
    if days > (5 - relax_days):
        return False
    # time constraint
    hours = {hour for _, hour in all_slots.keys()} if all_slots else set()
    if hours:
        if min(hours) < start_hour or max(hours) > end_hour:
            return False
    return True


def validate_same_tens(group: int, subgroup: int) -> bool:
    return group // 10 == subgroup // 10


def generate_url(combo: Dict[str, Any], quad: str) -> str:
    base = "https://www.fib.upc.edu/en/studies/bachelors-degrees/bachelor-degree-informatics-engineering/timetables"
    params = f"?&class=true&lang=true&quad={quad}"
    parts = []
    for subj, grp_info in combo.items():
        parts.append(f"a={subj}_{grp_info['group']}")
        parts.append(f"a={subj}_{grp_info['subgroup']}")
    return base + params + "&" + "&".join(parts)


def get_schedule_combinations(
    quad: str,
    subjects: List[str],
    start_hour: int,
    end_hour: int,
    languages: List[str],
    same_subgroup_as_group: bool,
    relax_days: int,
    blacklisted_groups: List[List[Any]],
    name_language: str = "",
) -> Dict[str, Any]:
    # setup language
    if not name_language:
        name_language = LANGUAGE_MAPPING.get("", "ca")
    end_hour -= 1
    langs = languages[:] + ["Per determinar"]
    logger.debug(
        "Params: %s, %s, %d, %d, %s, %s, %d, %s, %s",
        quad,
        subjects,
        start_hour,
        end_hour,
        languages,
        same_subgroup_as_group,
        relax_days,
        blacklisted_groups,
        name_language,
    )

    raw = fetch_classes_data_with_language(quad, name_language)
    parsed = parse_classes_data(raw)
    # debug: show parsed subjects and group counts
    logger.debug("Parsed subjects and group counts:")
    for subj, groups in parsed.items():
        logger.debug("  %s: %d group entries", subj, len(groups))

    # split schedules
    group_schedule = {}
    subgroup_schedule = {}
    # Populate subgroup entries and corresponding main groups
    for subj, groups in parsed.items():
        for gstr, classes in groups.items():
            if not gstr.isdigit():
                continue
            g = int(gstr)
            if g % 10 != 0:
                # subgroup session
                subgroup_schedule.setdefault(subj, {})[gstr] = classes
                # include the matching main group
                main = str(g - (g % 10))
                if main in parsed[subj]:
                    group_schedule.setdefault(subj, {})[main] = parsed[subj][main]
    # debug: show group and subgroup schedule for requested subjects
    logger.debug(
        "Group schedule contents: %s",
        {s: list(group_schedule.get(s, {}).keys()) for s in subjects},
    )
    logger.debug(
        "Subgroup schedule contents: %s",
        {s: list(subgroup_schedule.get(s, {}).keys()) for s in subjects},
    )

    # generate group combinations
    avail_groups = {
        s: list(group_schedule[s].keys()) for s in subjects if s in group_schedule
    }
    logger.debug("Available group options per subject: %s", avail_groups)
    group_combos = [
        dict(zip(avail_groups.keys(), prod))
        for prod in itertools.product(*avail_groups.values())
    ]
    valid_groups = []
    for combo in group_combos:
        if is_valid_schedule(
            group_schedule, combo, blacklisted_groups, langs, start_hour, end_hour
        ):
            valid_groups.append(combo)
    logger.debug("Valid group combinations count: %d", len(valid_groups))

    # generate subgroup combinations
    avail_subs = {
        s: list(subgroup_schedule[s].keys()) for s in subjects if s in subgroup_schedule
    }
    logger.debug("Available subgroup options per subject: %s", avail_subs)
    sub_combos = [
        dict(zip(avail_subs.keys(), prod))
        for prod in itertools.product(*avail_subs.values())
    ]
    valid_subs = []
    for combo in sub_combos:
        if is_valid_schedule(
            subgroup_schedule, combo, blacklisted_groups, langs, start_hour, end_hour
        ):
            valid_subs.append(combo)
    logger.debug("Valid subgroup combinations count: %d", len(valid_subs))

    # merge
    timetables = []
    urls = []
    for gcombo in valid_groups:
        for scombo in valid_subs:
            if not has_valid_schedule(
                get_time_slots(group_schedule, gcombo),
                get_time_slots(subgroup_schedule, scombo),
                relax_days,
                start_hour,
                end_hour,
            ):
                continue
            if same_subgroup_as_group:
                if not all(
                    validate_same_tens(
                        int(gcombo[subj]), int(scombo.get(subj, gcombo[subj]))
                    )
                    for subj in gcombo
                ):
                    continue
            merged = {}
            for subj in gcombo:
                sub = int(scombo.get(subj, gcombo[subj]))
                merged[subj] = {"group": int(gcombo[subj]), "subgroup": sub}
            merged_url = generate_url(merged, quad)
            merged["url"] = merged_url
            timetables.append(merged)
            urls.append(merged_url)

    result = {
        "total": len(timetables),
        "timetables": timetables,
        "subjects": subjects,
        "urls": urls,
    }
    logger.debug("Found %d schedules", len(timetables))
    return result
