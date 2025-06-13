# Schedule Generation Algorithm

Detailed documentation of the core algorithm that generates valid schedule combinations for FIB Manager.

## Algorithm Overview

The schedule generation algorithm is the heart of FIB Manager, responsible for finding all valid combinations of class groups and subgroups that satisfy user constraints. It implements a constraint satisfaction problem (CSP) solver optimized for academic scheduling.

### High-Level Process

```
1. Data Acquisition
   ├── Fetch class data from UPC API
   ├── Parse and normalize data structures
   └── Extract available groups/subgroups per subject

2. Constraint Definition
   ├── Time range constraints (start/end hours)
   ├── Language preferences
   ├── Day limitations
   ├── Blacklisted groups
   └── Dead hours limits

3. Combination Generation
   ├── Generate all possible group combinations
   ├── Apply subgroup constraints
   ├── Validate time conflicts
   └── Calculate dead hours

4. Filtering and Optimization
   ├── Apply user constraints
   ├── Sort by preferences (groups vs dead hours)
   ├── Generate schedule URLs
   └── Format output
```

## Core Algorithm Implementation

### Phase 1: Data Preparation

**Input Processing:**
```python
def prepare_schedule_data(subjects: List[str], quad: str, lang: str) -> Dict[str, Any]:
    """
    Prepare and normalize schedule data for processing.
    
    Args:
        subjects: List of subject codes to process
        quad: Quadrimester code (e.g., "2024Q1")
        lang: Language preference for API calls
    
    Returns:
        Dictionary containing normalized schedule data
    """
    # 1. Fetch raw data from API
    raw_data = fetch_classes_data(quad, lang)
    
    # 2. Parse into structured format
    parsed_data = parse_classes_data(raw_data)
    
    # 3. Filter for requested subjects only
    filtered_data = {
        subject: data for subject, data in parsed_data.items() 
        if subject in subjects
    }
    
    # 4. Validate data completeness
    validate_subject_availability(subjects, filtered_data)
    
    return filtered_data
```

**Data Structure After Parsing:**
```python
{
  "IES": {
    "101": {  # Group number
      "111": [  # Subgroup number
        {
          "subject": "IES",
          "group": 101,
          "subgroup": 111,
          "type": "T",  # Theory/Lab/Problems
          "start_hour": 8,
          "end_hour": 10,
          "day": 1,  # Monday=1, Tuesday=2, etc.
          "language": "en"
        }
      ]
    }
  }
}
```

### Phase 2: Constraint Application

**Time Range Filtering:**
```python
def apply_time_constraints(data: Dict, start_hour: int, end_hour: int) -> Dict:
    """
    Filter classes that fall within acceptable time range.
    
    Algorithm:
    - Remove classes that start before start_hour
    - Remove classes that end after end_hour
    - Preserve group/subgroup structure
    """
    filtered_data = {}
    
    for subject, groups in data.items():
        filtered_groups = {}
        
        for group_num, subgroups in groups.items():
            filtered_subgroups = {}
            
            for subgroup_num, sessions in subgroups.items():
                valid_sessions = [
                    session for session in sessions
                    if start_hour <= session["start_hour"] and session["end_hour"] <= end_hour
                ]
                
                if valid_sessions:  # Only keep subgroups with valid sessions
                    filtered_subgroups[subgroup_num] = valid_sessions
            
            if filtered_subgroups:  # Only keep groups with valid subgroups
                filtered_groups[group_num] = filtered_subgroups
        
        if filtered_groups:  # Only keep subjects with valid groups
            filtered_data[subject] = filtered_groups
    
    return filtered_data
```

**Language Filtering:**
```python
def apply_language_constraints(data: Dict, languages: List[str]) -> Dict:
    """
    Filter classes by preferred languages.
    
    Algorithm:
    - Check each session's language against preferences
    - Remove entire subgroups if no sessions match
    - Preserve structure hierarchy
    """
    if not languages:  # No language preference = accept all
        return data
    
    normalized_langs = [normalize_language(lang) for lang in languages]
    
    # Filter sessions by language preference
    # Implementation similar to time constraints but checking language field
    return filtered_data
```

### Phase 3: Combination Generation

**Core Combination Algorithm:**
```python
def generate_combinations(data: Dict, same_subgroup: bool, blacklist: List[str]) -> List[Dict]:
    """
    Generate all valid combinations of groups and subgroups.
    
    Args:
        data: Parsed and filtered schedule data
        same_subgroup: Whether subgroups must match group tens digit
        blacklist: List of "SUBJECT-GROUP" pairs to exclude
    
    Returns:
        List of valid combinations
    """
    subjects = list(data.keys())
    combinations = []
    
    # 1. Generate group combinations (Cartesian product)
    group_options = []
    for subject in subjects:
        subject_groups = list(data[subject].keys())
        group_options.append([(subject, group) for group in subject_groups])
    
    # 2. Generate all possible group combinations
    import itertools
    group_combinations = itertools.product(*group_options)
    
    # 3. For each group combination, generate subgroup combinations
    for group_combo in group_combinations:
        # Check blacklist
        if is_blacklisted(group_combo, blacklist):
            continue
        
        # Generate subgroup combinations for this group combination
        subgroup_combos = generate_subgroup_combinations(
            data, group_combo, same_subgroup
        )
        
        # 4. Validate each combination for time conflicts
        for subgroup_combo in subgroup_combos:
            if is_valid_combination(data, group_combo, subgroup_combo):
                combination = create_combination_object(
                    data, group_combo, subgroup_combo
                )
                combinations.append(combination)
    
    return combinations
```

**Subgroup Generation Logic:**
```python
def generate_subgroup_combinations(data: Dict, group_combo: List, same_subgroup: bool) -> List:
    """
    Generate valid subgroup combinations for a given group combination.
    
    Args:
        data: Schedule data
        group_combo: Selected group combination
        same_subgroup: Subgroup constraint flag
    
    Returns:
        List of valid subgroup combinations
    """
    subgroup_options = []
    
    for subject, group in group_combo:
        available_subgroups = list(data[subject][group].keys())
        
        if same_subgroup:
            # Filter subgroups to match group tens digit
            group_tens = int(group) // 10 * 10  # e.g., 101 -> 100
            valid_subgroups = [
                sg for sg in available_subgroups
                if int(sg) // 10 * 10 == group_tens
            ]
        else:
            valid_subgroups = available_subgroups
        
        subgroup_options.append(valid_subgroups)
    
    # Generate all combinations of valid subgroups
    import itertools
    return list(itertools.product(*subgroup_options))
```

### Phase 4: Conflict Detection

**Time Conflict Validation:**
```python
def is_valid_combination(data: Dict, group_combo: List, subgroup_combo: List) -> bool:
    """
    Check if a combination has time conflicts.
    
    Algorithm:
    1. Collect all sessions from the combination
    2. Check for overlapping time slots
    3. Return False if any conflicts found
    """
    all_sessions = []
    
    # Collect all sessions from the combination
    for i, (subject, group) in enumerate(group_combo):
        subgroup = subgroup_combo[i]
        sessions = data[subject][group][subgroup]
        all_sessions.extend(sessions)
    
    # Check for time conflicts
    for i in range(len(all_sessions)):
        for j in range(i + 1, len(all_sessions)):
            if sessions_overlap(all_sessions[i], all_sessions[j]):
                return False
    
    return True

def sessions_overlap(session1: Dict, session2: Dict) -> bool:
    """
    Check if two sessions have overlapping time slots.
    
    Sessions overlap if:
    - Same day AND
    - Time ranges intersect
    """
    if session1["day"] != session2["day"]:
        return False
    
    # Check time overlap
    start1, end1 = session1["start_hour"], session1["end_hour"]
    start2, end2 = session2["start_hour"], session2["end_hour"]
    
    # Two ranges overlap if: max(start1, start2) < min(end1, end2)
    return max(start1, start2) < min(end1, end2)
```

### Phase 5: Dead Hours Calculation

**Dead Hours Algorithm:**
```python
def calculate_dead_hours(sessions: List[Dict]) -> int:
    """
    Calculate total dead hours (gaps between classes) in a schedule.
    
    Algorithm:
    1. Group sessions by day
    2. For each day, sort sessions by start time
    3. Calculate gaps between consecutive sessions
    4. Sum all gaps across all days
    """
    dead_hours = 0
    
    # Group sessions by day
    days = {}
    for session in sessions:
        day = session["day"]
        if day not in days:
            days[day] = []
        days[day].append(session)
    
    # Calculate dead hours for each day
    for day, day_sessions in days.items():
        # Sort sessions by start time
        sorted_sessions = sorted(day_sessions, key=lambda s: s["start_hour"])
        
        # Calculate gaps between consecutive sessions
        for i in range(len(sorted_sessions) - 1):
            current_end = sorted_sessions[i]["end_hour"]
            next_start = sorted_sessions[i + 1]["start_hour"]
            
            if next_start > current_end:
                dead_hours += next_start - current_end
    
    return dead_hours
```

### Phase 6: Optimization and Sorting

**Sorting Strategies:**
```python
def sort_schedules_by_mode(schedules: List[Dict], sort_mode: str, 
                          group_schedule: Dict, subgroup_schedule: Dict) -> List[Dict]:
    """
    Sort schedules according to user preference.
    
    Sort Modes:
    - "groups": Minimize number of different groups
    - "dead_hours": Minimize dead hours between classes
    """
    if sort_mode == "groups":
        return sort_by_group_count(schedules, group_schedule, subgroup_schedule)
    elif sort_mode == "dead_hours":
        return sort_by_dead_hours(schedules)
    else:
        return schedules

def sort_by_group_count(schedules: List[Dict], group_schedule: Dict, 
                       subgroup_schedule: Dict) -> List[Dict]:
    """
    Sort by total number of groups and subgroups.
    
    Priority:
    1. Fewer total groups (across all subjects)
    2. Fewer total subgroups
    3. Fewer dead hours (tiebreaker)
    """
    def group_count_key(schedule):
        subjects = schedule.get("subjects", {})
        
        # Count unique groups and subgroups
        groups = set(info.get("group") for info in subjects.values())
        subgroups = set(info.get("subgroup") for info in subjects.values())
        
        return (
            len(groups),           # Primary: fewer groups
            len(subgroups),        # Secondary: fewer subgroups  
            schedule.get("dead_hours", 0)  # Tiebreaker: fewer dead hours
        )
    
    return sorted(schedules, key=group_count_key)

def sort_by_dead_hours(schedules: List[Dict]) -> List[Dict]:
    """
    Sort by dead hours, then by group count.
    """
    def dead_hours_key(schedule):
        return (
            schedule.get("dead_hours", 0),    # Primary: fewer dead hours
            len(schedule.get("subjects", {})) # Tiebreaker: fewer subjects
        )
    
    return sorted(schedules, key=dead_hours_key)
```

## Performance Optimizations

### Algorithmic Optimizations

**Early Termination:**
```python
def generate_combinations_optimized(data: Dict, max_dead_hours: int = -1) -> List[Dict]:
    """
    Optimized combination generation with early termination.
    
    Optimizations:
    1. Early conflict detection during generation
    2. Dead hours pruning during validation
    3. Blacklist checking before expensive operations
    """
    combinations = []
    
    for group_combo in generate_group_combinations(data):
        # Early blacklist check
        if is_blacklisted_fast(group_combo):
            continue
        
        for subgroup_combo in generate_subgroup_combinations(data, group_combo):
            # Early conflict detection
            if has_obvious_conflicts(group_combo, subgroup_combo):
                continue
            
            # Full validation only for promising combinations
            if is_valid_combination(data, group_combo, subgroup_combo):
                combination = create_combination_object(data, group_combo, subgroup_combo)
                
                # Dead hours pruning
                if max_dead_hours >= 0 and combination["dead_hours"] > max_dead_hours:
                    continue
                
                combinations.append(combination)
    
    return combinations
```

**Memory Optimization:**
```python
def generate_combinations_memory_efficient(data: Dict) -> Iterator[Dict]:
    """
    Memory-efficient generator that yields combinations one at a time.
    
    Benefits:
    - Reduces memory usage for large result sets
    - Allows early termination by caller
    - Enables streaming processing
    """
    for group_combo in generate_group_combinations(data):
        for subgroup_combo in generate_subgroup_combinations(data, group_combo):
            if is_valid_combination(data, group_combo, subgroup_combo):
                yield create_combination_object(data, group_combo, subgroup_combo)
```

### Caching Strategies

**Validation Caching:**
```python
class ValidationCache:
    """Cache validation results to avoid recomputation."""
    
    def __init__(self):
        self.conflict_cache = {}
        self.dead_hours_cache = {}
    
    def check_conflicts_cached(self, combination_key: str, sessions: List[Dict]) -> bool:
        """Check conflicts with caching."""
        if combination_key not in self.conflict_cache:
            self.conflict_cache[combination_key] = has_conflicts(sessions)
        return self.conflict_cache[combination_key]
    
    def calculate_dead_hours_cached(self, combination_key: str, sessions: List[Dict]) -> int:
        """Calculate dead hours with caching."""
        if combination_key not in self.dead_hours_cache:
            self.dead_hours_cache[combination_key] = calculate_dead_hours(sessions)
        return self.dead_hours_cache[combination_key]
```

## Algorithm Complexity Analysis

### Time Complexity

**Worst Case Analysis:**
- Let `n` = number of subjects
- Let `g` = average groups per subject  
- Let `s` = average subgroups per group

**Combination Generation:**
- Group combinations: `O(g^n)`
- Subgroup combinations per group combo: `O(s^n)`
- Total combinations: `O((g×s)^n)`

**Validation:**
- Conflict checking per combination: `O(k²)` where `k` = total sessions
- Dead hours calculation: `O(k×log(k))` for sorting

**Overall Complexity:** `O((g×s)^n × k²)`

**Practical Performance:**
- For typical usage (3-5 subjects): Very fast (< 1 second)
- For heavy usage (8-10 subjects): Moderate (1-5 seconds)
- For extreme usage (>10 subjects): Slow (>10 seconds)

### Space Complexity

**Memory Usage:**
- Input data: `O(n×g×s×k)` 
- Combination storage: `O((g×s)^n)`
- Validation caches: `O((g×s)^n)`

**Optimization Impact:**
- Generator pattern: `O(1)` for combination storage
- Validation caching: Trades memory for computation time
- Early termination: Reduces average case significantly

## Edge Cases and Special Handling

### Data Quality Issues

**Missing Data Handling:**
```python
def handle_missing_data(data: Dict, subjects: List[str]) -> Dict:
    """
    Handle cases where subjects have no available groups/subgroups.
    
    Strategies:
    1. Log missing subjects for user awareness
    2. Continue processing with available subjects
    3. Provide informative error messages
    """
    available_subjects = set(data.keys())
    requested_subjects = set(subjects)
    missing_subjects = requested_subjects - available_subjects
    
    if missing_subjects:
        logger.warning(f"Subjects not available: {missing_subjects}")
    
    # Filter to only process available subjects
    return {subject: data[subject] for subject in subjects if subject in data}
```

**Malformed Schedule Data:**
```python
def validate_schedule_data(data: Dict) -> Dict:
    """
    Validate and clean malformed schedule data.
    
    Checks:
    1. Valid time ranges (start < end)
    2. Valid day numbers (1-7)
    3. Complete session information
    """
    cleaned_data = {}
    
    for subject, groups in data.items():
        cleaned_groups = {}
        
        for group, subgroups in groups.items():
            cleaned_subgroups = {}
            
            for subgroup, sessions in subgroups.items():
                valid_sessions = []
                
                for session in sessions:
                    if is_valid_session(session):
                        valid_sessions.append(session)
                    else:
                        logger.warning(f"Invalid session data: {session}")
                
                if valid_sessions:
                    cleaned_subgroups[subgroup] = valid_sessions
            
            if cleaned_subgroups:
                cleaned_groups[group] = cleaned_subgroups
        
        if cleaned_groups:
            cleaned_data[subject] = cleaned_groups
    
    return cleaned_data
```

### Constraint Conflicts

**Impossible Constraint Combinations:**
```python
def detect_impossible_constraints(data: Dict, constraints: Dict) -> List[str]:
    """
    Detect constraint combinations that make scheduling impossible.
    
    Returns list of conflict descriptions for user feedback.
    """
    conflicts = []
    
    # Check if time constraints eliminate all classes
    if constraints["start_hour"] >= constraints["end_hour"]:
        conflicts.append("Invalid time range: start hour must be before end hour")
    
    # Check if language constraints eliminate all options
    available_languages = get_available_languages(data)
    requested_languages = set(constraints["languages"])
    if requested_languages and not (requested_languages & available_languages):
        conflicts.append(f"No classes available in requested languages: {requested_languages}")
    
    # Check if day constraints are too restrictive
    required_days = estimate_required_days(data)
    if constraints["max_days"] < required_days:
        conflicts.append(f"Requested max days ({constraints['max_days']}) less than required ({required_days})")
    
    return conflicts
```

## Testing and Validation

### Algorithm Testing

**Unit Tests for Core Functions:**
```python
def test_combination_generation():
    """Test basic combination generation logic."""
    test_data = create_test_schedule_data()
    combinations = generate_combinations(test_data, same_subgroup=True, blacklist=[])
    
    assert len(combinations) > 0
    assert all(is_valid_combination_structure(combo) for combo in combinations)

def test_conflict_detection():
    """Test time conflict detection."""
    overlapping_sessions = [
        {"day": 1, "start_hour": 8, "end_hour": 10},
        {"day": 1, "start_hour": 9, "end_hour": 11}  # Overlaps with first
    ]
    
    assert sessions_overlap(overlapping_sessions[0], overlapping_sessions[1])

def test_dead_hours_calculation():
    """Test dead hours calculation."""
    sessions = [
        {"day": 1, "start_hour": 8, "end_hour": 10},
        {"day": 1, "start_hour": 12, "end_hour": 14}  # 2-hour gap
    ]
    
    assert calculate_dead_hours(sessions) == 2
```

**Integration Tests:**
```python
def test_full_schedule_generation():
    """Test complete schedule generation workflow."""
    subjects = ["IES", "XC"]
    result = get_schedule_combinations(
        quad="2024Q1",
        subjects=subjects,
        start_hour=8,
        end_hour=20,
        languages=["en"],
        same_subgroup=True,
        relax_days=0,
        blacklisted=[],
        max_dead_hours=-1
    )
    
    assert "schedules" in result
    assert isinstance(result["schedules"], list)
    assert result["total_schedules"] == len(result["schedules"])
```

### Performance Testing

**Benchmark Tests:**
```python
import time

def benchmark_algorithm_performance():
    """Benchmark algorithm performance with varying input sizes."""
    test_cases = [
        {"subjects": 2, "groups_per_subject": 3, "subgroups_per_group": 2},
        {"subjects": 5, "groups_per_subject": 4, "subgroups_per_group": 3},
        {"subjects": 8, "groups_per_subject": 5, "subgroups_per_group": 4}
    ]
    
    for case in test_cases:
        test_data = generate_test_data(case)
        
        start_time = time.time()
        combinations = generate_combinations(test_data, True, [])
        end_time = time.time()
        
        print(f"Subjects: {case['subjects']}, "
              f"Combinations: {len(combinations)}, "
              f"Time: {end_time - start_time:.2f}s")
```

## Future Improvements

### Algorithmic Enhancements

1. **Parallel Processing:** Distribute combination generation across multiple cores
2. **Heuristic Pruning:** Use domain knowledge to eliminate unlikely combinations early
3. **Incremental Updates:** Cache results and update only when data changes
4. **Machine Learning:** Learn user preferences to prioritize better schedules

### Performance Optimizations

1. **Just-in-Time Compilation:** Use NumPy or Numba for hot path optimization
2. **Database Integration:** Store and query combinations using SQL
3. **Streaming API:** Process combinations as they're generated
4. **Progressive Enhancement:** Return partial results while continuing computation

### User Experience Improvements

1. **Real-time Feedback:** Show progress during long computations
2. **Smart Defaults:** Learn from user behavior to suggest better constraints
3. **Constraint Relaxation:** Automatically suggest constraint modifications when no results found
4. **Visual Algorithm:** Show how combinations are built step by step
