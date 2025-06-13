# Examples and Use Cases

Comprehensive collection of practical examples and real-world use cases for FIB Manager, demonstrating various features and scenarios.

## Basic Use Cases

### 1. Simple Schedule Search

**Scenario:** Find any valid schedule for two subjects.

```cmd
REM Basic schedule search for IES and XC
fib-manager schedules -s IES XC
```

**Expected Output:**
```json
{
  "quadrimester": "2024Q2",
  "subjects": ["IES", "XC"],
  "total_schedules": 8,
  "schedules": [
    {
      "id": 1,
      "subjects": {
        "IES": {"group": 101, "subgroup": 111},
        "XC": {"group": 201, "subgroup": 211}
      },
      "dead_hours": 0,
      "url": "https://raco.fib.upc.edu/...",
      "sessions": [...]
    }
  ]
}
```

**Use Case:** Quick verification that subjects can be combined without conflicts.

### 2. Time-Constrained Schedule

**Scenario:** Student prefers morning classes only.

```cmd
REM Find schedules that end by 2 PM
fib-manager schedules -s IES XC PROP --start 8 --end 14
```

**Benefits:**
- Avoids late afternoon classes
- Leaves time for work or personal activities
- Reduces commuting during peak hours

### 3. Language Preference

**Scenario:** International student prefers English classes.

```cmd
REM Find schedules with English classes only
fib-manager schedules -s IES XC -l en

REM Allow English and Spanish, but not Catalan
fib-manager schedules -s IES XC -l en es
```

**Real-world Context:**
- Erasmus students with limited Catalan knowledge
- Better understanding of technical concepts in familiar language
- Improved academic performance

## Advanced Scheduling Scenarios

### 4. Part-time Student Schedule

**Scenario:** Working student needs compact schedule.

```cmd
REM Maximum 3 days on campus, morning classes only
fib-manager schedules -s IES XC PROP --days 3 --start 8 --end 14 --sort dead-hours
```

**Strategy Explanation:**
- `--days 3`: Minimize campus days for work flexibility
- `--start 8 --end 14`: Morning schedule for afternoon work
- `--sort dead-hours`: Minimize gaps for efficient time use

### 5. Avoiding Specific Groups

**Scenario:** Student heard negative feedback about certain professors.

```cmd
REM Avoid specific groups based on professor feedback
fib-manager schedules -s IES XC --blacklist IES-101 XC-205
```

**Extended Example:**
```cmd
REM Complex blacklist with multiple constraints
fib-manager schedules -s IES XC PROP BD ^
  --blacklist IES-101 XC-205 PROP-301 ^
  --days 4 ^
  --start 9 --end 18 ^
  -l en es
```

### 6. Flexible Subgroup Assignment

**Scenario:** Maximize schedule options with relaxed subgroup rules.

```cmd
REM Allow different subgroup assignments for more flexibility
fib-manager schedules -s IES XC PROP --freedom --sort dead-hours
```

**Explanation:**
- By default, subgroups must match group tens (101 → 11X)
- `--freedom` allows any subgroup assignment
- Increases possible combinations significantly
- Useful when facing limited options

## Interactive Mode Examples

### 7. Guided Schedule Planning

**Scenario:** New user wants guided experience.

```cmd
REM Start interactive mode
fib-manager app
```

**Interactive Flow:**
1. **Subject Selection:** Browse available subjects with descriptions
2. **Preference Setup:** Configure time, language, and day preferences
3. **Schedule Review:** Navigate through valid combinations
4. **Browser Integration:** Open preferred schedule in web browser

**Benefits:**
- User-friendly for beginners
- Visual feedback during selection
- Immediate validation of choices
- Seamless transition to official UPC interface

### 8. Subject Exploration

**Scenario:** Student exploring available courses.

```cmd
REM Interactive subject browser
fib-manager subjects -v

REM Or command-line subject listing
fib-manager subjects -q 2024Q1 -l en
```

**Use Cases:**
- Course planning for future quadrimesters
- Exploring elective options
- Verifying subject availability
- Multi-language course name reference

## Grade Calculator Examples

### 9. Simple Grade Planning

**Scenario:** Student needs specific grade on final exam.

```cmd
REM Calculate required final exam grade
fib-manager marks ^
  --formula "LAB*0.3 + MIDTERM*0.3 + FINAL*0.4" ^
  --target 7.0 ^
  --values LAB=8.5 MIDTERM=6.0
```

**Expected Output:**
```json
{
  "formula": "LAB*0.3 + MIDTERM*0.3 + FINAL*0.4",
  "target": 7.0,
  "known_values": {"LAB": 8.5, "MIDTERM": 6.0},
  "missing_variables": ["FINAL"],
  "solution": {"FINAL": 6.25},
  "result": 7.0
}
```

**Interpretation:** Student needs 6.25 on final exam to achieve overall grade of 7.0.

### 10. Complex Grading Formula

**Scenario:** Course with complex conditional grading.

```cmd
REM Course that takes maximum of weighted average and minimum exam
fib-manager marks ^
  --formula "max(0.4*EX1 + 0.6*EX2, min(EX1, EX2))" ^
  --target 5.0 ^
  --values EX1=4.0
```

**Real-world Context:**
- Many FIB courses have conditional passing requirements
- Must pass both individual exams AND achieve overall average
- Helps students understand minimum requirements

### 11. Interactive Grade Planning

**Scenario:** Student wants to explore different grade scenarios.

```cmd
REM Launch interactive grade calculator
fib-manager marks --view
```

**Interactive Features:**
- Enter formula with validation
- Input known grades step by step
- See real-time calculations
- Explore "what-if" scenarios

## Workflow Integration Examples

### 12. Automated Schedule Generation

**Scenario:** Create script for regular schedule checking.

```cmd
REM Windows batch script for schedule automation
@echo off
echo Checking schedules for 2024Q2...

fib-manager schedules -s IES XC PROP BD ^
  --start 9 --end 18 ^
  -l en ^
  --days 4 ^
  --sort dead-hours > schedules_2024Q2.json

echo Schedule results saved to schedules_2024Q2.json
```

**Use Cases:**
- Monitor schedule changes throughout enrollment period
- Generate reports for course planning
- Automate schedule comparison between quadrimesters

### 13. Data Export and Analysis

**Scenario:** Export data for external analysis.

```cmd
REM Export subject data for analysis
fib-manager subjects -q 2024Q1 -l en > subjects_2024Q1.json

REM Export schedule data
fib-manager schedules -s IES XC PROP > schedule_options.json
```

**Integration Examples:**
```cmd
REM Pipe to jq for JSON processing
fib-manager subjects | jq ".subjects | keys[]"

REM Count available schedules
fib-manager schedules -s IES XC | jq ".total_schedules"

REM Extract subjects with least dead hours
fib-manager schedules -s IES XC PROP | jq ".schedules[0]"
```

## Troubleshooting Examples

### 14. No Schedules Found

**Problem:** Schedule search returns no results.

```cmd
REM Overly restrictive constraints
fib-manager schedules -s IES XC PROP BD SO --days 2 --start 10 --end 12
```

**Solution Approach:**
```cmd
REM 1. Check individual subjects exist
fib-manager subjects | findstr "IES XC PROP BD SO"

REM 2. Relax time constraints
fib-manager schedules -s IES XC PROP BD SO --days 3 --start 8 --end 18

REM 3. Remove language restrictions
fib-manager schedules -s IES XC PROP BD SO --days 3

REM 4. Allow subgroup flexibility
fib-manager schedules -s IES XC PROP BD SO --freedom
```

### 15. API Connection Issues

**Problem:** Cannot connect to UPC API.

```cmd
REM Test basic connectivity
fib-manager subjects
```

**Debugging Steps:**
```cmd
REM Enable debug mode
set FIB_DEBUG=true
fib-manager subjects

REM Check specific quadrimester
fib-manager subjects -q 2024Q1

REM Test with different language
fib-manager subjects -l es
```

**Expected Debug Output:**
```
2024-06-13 10:30:15 DEBUG Making request to: https://raco.fib.upc.edu/api/...
2024-06-13 10:30:16 DEBUG Response status: 200
2024-06-13 10:30:16 DEBUG Response size: 15432 bytes
```

## Real Student Scenarios

### 16. Erasmus Student Planning

**Background:** International student, limited Catalan, prefers compact schedule.

```cmd
REM Erasmus student schedule optimization
fib-manager schedules -s IES XC PROP ^
  -l en es ^
  --days 3 ^
  --start 9 --end 17 ^
  --sort dead-hours ^
  -v
```

**Considerations:**
- Language barrier requires English/Spanish classes
- Cultural adjustment benefits from shorter campus days
- Interactive mode helps with navigation
- Browser integration connects to official enrollment

### 17. Working Student Optimization

**Background:** Student works part-time afternoons, needs morning schedule.

```cmd
REM Working student morning schedule
fib-manager schedules -s IES XC BD ^
  --start 8 --end 14 ^
  --days 4 ^
  --sort groups
```

**Strategy:**
- Morning-only classes for afternoon work
- Minimize days on campus
- Prioritize fewer groups for consistency

### 18. Final Year Student

**Background:** Experienced student taking advanced courses with specific requirements.

```cmd
REM Advanced student with complex requirements
fib-manager schedules -s TFG PAR PROP ^
  --blacklist TFG-401 PAR-501 ^
  --freedom ^
  -l en ^
  --max-dead-hours 3
```

**Considerations:**
- Specific professor preferences (blacklist)
- Flexibility in subgroup assignment
- Quality over quantity (limited dead hours)
- English for international collaboration

## Performance and Scale Examples

### 19. Maximum Subject Load

**Scenario:** Testing system limits with many subjects.

```cmd
REM Heavy course load (system stress test)
fib-manager schedules -s IES XC PROP BD SO ASO ^
  --start 8 --end 20 ^
  --freedom
```

**Performance Expectations:**
- 6 subjects: ~10-30 seconds
- Memory usage: ~100-500 MB
- Result count: Potentially thousands

### 20. Optimization Comparison

**Scenario:** Compare different optimization strategies.

```cmd
REM Compare sorting strategies
fib-manager schedules -s IES XC PROP --sort groups > groups_first.json
fib-manager schedules -s IES XC PROP --sort dead-hours > dead_hours_first.json

REM Analyze results
type groups_first.json | jq ".schedules[0]"
type dead_hours_first.json | jq ".schedules[0]"
```

## Command Combinations and Workflows

### 21. Complete Planning Workflow

**Scenario:** Full semester planning process.

```cmd
REM Step 1: Explore available subjects
fib-manager subjects -q 2024Q2 -v

REM Step 2: Generate initial schedule options
fib-manager schedules -s IES XC PROP BD --days 4 -v

REM Step 3: Refine with constraints
fib-manager schedules -s IES XC PROP BD ^
  --days 4 ^
  --start 9 --end 18 ^
  --blacklist IES-101 ^
  --sort dead-hours

REM Step 4: Plan grade requirements
fib-manager marks ^
  --formula "LAB*0.4 + EXAM*0.6" ^
  --target 7.0 ^
  --values LAB=8.0
```

### 22. Comparative Analysis

**Scenario:** Compare different subject combinations.

```cmd
REM Option A: Core subjects only
fib-manager schedules -s IES XC PROP > option_a.json

REM Option B: Core + elective
fib-manager schedules -s IES XC PROP BD > option_b.json

REM Option C: Alternative elective
fib-manager schedules -s IES XC PROP SO > option_c.json

REM Compare results
echo Option A schedules:
type option_a.json | jq ".total_schedules"
echo Option B schedules:
type option_b.json | jq ".total_schedules"
echo Option C schedules:
type option_c.json | jq ".total_schedules"
```

## Integration with External Tools

### 23. Calendar Integration

**Scenario:** Export schedule to calendar format.

```cmd
REM Generate schedule data for calendar import
fib-manager schedules -s IES XC --sort dead-hours > schedule.json

REM Process with external script (pseudo-code)
python convert_to_ical.py schedule.json > schedule.ics
```

### 24. Notification System

**Scenario:** Monitor for schedule changes.

```cmd
REM Create monitoring script
@echo off
:loop
fib-manager schedules -s IES XC PROP > current_schedule.json
fc /B current_schedule.json previous_schedule.json > nul
if errorlevel 1 (
    echo Schedule changed! New options available.
    copy current_schedule.json previous_schedule.json
)
timeout /t 3600 > nul
goto loop
```

## Tips and Best Practices

### 25. Efficient Usage Patterns

**Quick Checks:**
```cmd
REM Fast subject availability check
fib-manager subjects -q 2024Q2 | findstr "IES XC"

REM Quick schedule count
fib-manager schedules -s IES XC | jq ".total_schedules"
```

**Gradual Constraint Application:**
```cmd
REM Start broad, then narrow down
fib-manager schedules -s IES XC PROP
fib-manager schedules -s IES XC PROP --days 4
fib-manager schedules -s IES XC PROP --days 4 --start 9
fib-manager schedules -s IES XC PROP --days 4 --start 9 --end 18
```

**Performance Optimization:**
```cmd
REM Use specific quadrimester to avoid auto-detection
fib-manager schedules -s IES XC -q 2024Q2

REM Sort by groups for faster generation
fib-manager schedules -s IES XC PROP --sort groups

REM Limit dead hours for early termination
fib-manager schedules -s IES XC PROP --max-dead-hours 2
```

### 26. Common Mistake Prevention

**Avoid These Patterns:**
```cmd
REM DON'T: Use too many subjects without constraints
REM fib-manager schedules -s IES XC PROP BD SO ASO TC

REM DO: Add reasonable constraints
fib-manager schedules -s IES XC PROP BD SO --days 4 --max-dead-hours 4

REM DON'T: Use impossible time ranges
REM fib-manager schedules -s IES XC --start 18 --end 10

REM DO: Use logical time ranges
fib-manager schedules -s IES XC --start 8 --end 18
```

**Validation Checks:**
```cmd
REM Always verify subjects exist first
fib-manager subjects | findstr "NEWSUBJECT"

REM Check if constraints are too restrictive
fib-manager schedules -s IES XC --days 1
REM If no results, try:
fib-manager schedules -s IES XC --days 2
```

## Advanced Integration Examples

### 27. Multi-Quadrimester Planning

**Scenario:** Plan multiple quadrimesters in advance.

```cmd
REM Compare subject availability across quadrimesters
fib-manager subjects -q 2024Q1 > subjects_q1.json
fib-manager subjects -q 2024Q2 > subjects_q2.json

REM Find common subjects
type subjects_q1.json | jq ".subjects | keys[]" > q1_subjects.txt
type subjects_q2.json | jq ".subjects | keys[]" > q2_subjects.txt
```

### 28. Group Analysis

**Scenario:** Analyze group distributions and patterns.

```cmd
REM Get detailed schedule information
fib-manager schedules -s IES XC PROP --sort groups > detailed_schedules.json

REM Extract group information for analysis
type detailed_schedules.json | jq ".schedules[].subjects | to_entries | .[] | {subject: .key, group: .value.group}"
```

These examples demonstrate the versatility and power of FIB Manager across various real-world scenarios. Users can adapt these patterns to their specific needs and combine commands for complex workflows.
