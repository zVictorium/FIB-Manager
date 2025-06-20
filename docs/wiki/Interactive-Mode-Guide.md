# Interactive Mode Guide

Complete guide to using FIB Manager's interactive console application, designed for users who prefer a guided, menu-driven interface.

## Overview

FIB Manager's interactive mode provides a user-friendly, guided experience with:
- **Visual Navigation**: Menu-driven interface with keyboard controls
- **Step-by-step Guidance**: Walks users through complex operations
- **Real-time Feedback**: Immediate validation and error messages
- **Rich Display**: Color-coded tables, progress indicators, and formatted output
- **Seamless Integration**: Direct links to official UPC schedule interface

## Launching Interactive Mode

### Starting the Application

```cmd
REM Launch interactive mode
fib-manager app
```

### System Requirements

**Supported Terminals:**
- **Windows**: Windows Terminal, PowerShell
- **macOS**: Terminal.app, iTerm2
- **Linux**: Most modern terminals with ANSI support

**Avoid:**
- Windows Command Prompt (cmd.exe) - limited interactive support
- Very old terminal applications without color support

### First Launch

When you first run interactive mode, you'll see:

1. **Splash Screen**: ASCII art logo and welcome message
2. **Main Menu**: Primary navigation options
3. **Status Information**: Current quadrimester and system status

## Main Menu Navigation

### Available Options

The main menu presents four primary options:

```
┌─────────────────────────────────────┐
│            FIB Manager              │
├─────────────────────────────────────┤
│  Search schedules                   │
│  List subjects                      │
│  Calculate marks                    │
│  Quit                               │
└─────────────────────────────────────┘
```

### Navigation Controls

| Key | Action |
|-----|--------|
| `↑` / `↓` | Navigate menu options |
| `Enter` | Select highlighted option |
| `Esc` | Go back to previous menu |
| `Q` | Quit application |

## Schedule Search Workflow

### Step 1: Subject Selection

**Process:**
1. Choose "Search schedules" from main menu
2. System loads available subjects for current quadrimester
3. Interactive checkbox interface appears with all subjects

**Subject Selection Interface:**
```
Select subjects:
❯ ◯ IES - Software Engineering
  ◯ XC - Computer Networks  
  ◯ PROP - Programming Project
  ◯ BD - Databases
  ◯ SO - Operating Systems
  
Use ↑↓, Space to toggle, Enter to confirm
```

**Features:**
- **Search Filter**: Type to filter subjects by code or name
- **Multi-select**: Select multiple subjects with spacebar
- **Validation**: Must select at least one subject to continue

### Step 2: Schedule Preferences

**Time Range Configuration:**
```
Starting hour (inclusive):
❯ 8
  9
  10
  11
  12

Ending hour (exclusive):
❯ 16
  17
  18
  19
  20
```

**Day Limitation Setup:**
```
Maximum days with classes:
❯ 3
  4
  5 (no limit)
```

**Language Preferences:**
```
Select languages of the classes:
❯ ☑ English
  ☑ Spanish
  ☐ Catalan
```

### Step 3: Advanced Options

**Subgroup Flexibility:**
```
Allow different subgroup than group?
❯ Yes
  No
```

**Group Blacklisting:**
- System displays available groups for selected subjects
- Users can blacklist specific groups based on preferences
- Useful for avoiding specific professors or time slots

**Dead Hours Limitation:**
```
Maximum dead hours allowed:
❯ No limit
  0
  1
  2
  3
```

### Step 4: Results Processing

**Generation Process:**
1. System displays progress indicator
2. Fetches real-time data from UPC API
3. Generates all valid combinations
4. Applies user constraints and filters
5. Sorts results by user preference

**Progress Display:**
```
Generating schedules...
[████████████████████████████████] 100%
Found 24 valid schedule combinations
```

## Schedule Viewer Interface

### Grid View

**Visual Schedule Display:**
```
Schedule 1/24                           Sort: Groups ↕ Dead Hours

┌──────┬─────────┬─────────┬─────────┬─────────┬─────────┐
│ Hour │ Monday  │ Tuesday │ Wed     │ Thursday│ Friday  │
├──────┼─────────┼─────────┼─────────┼─────────┼─────────┤
│ 8-9  │ IES(T)🇬🇧│         │ IES(T)🇬🇧│         │         │
│ 9-10 │ IES(T)🇬🇧│         │ IES(T)🇬🇧│         │         │
│10-11 │         │ XC(T)🇪🇸 │         │ XC(T)🇪🇸 │         │
│11-12 │         │ XC(T)🇪🇸 │         │ XC(T)🇪🇸 │         │
│12-13 │         │         │         │         │ XC(L)🇬🇧│
│13-14 │         │         │         │         │ XC(L)🇬🇧│
└──────┴─────────┴─────────┴─────────┴─────────┴─────────┘

Dead Hours: 0    Groups: IES-101, XC-201    URL: Available
```

**Display Elements:**
- **Color Coding**: Each subject has a distinct color
- **Class Types**: T(Theory), L(Laboratory), P(Problems)
- **Language Flags**: 🇬🇧(English), 🇪🇸(Spanish), 🇨🇦(Catalan)
- **Group Information**: Shows selected groups and subgroups
- **Statistics**: Dead hours count and URL availability

### Detailed View

**Group Information Table:**
```
Schedule 1/24 - Group Details

┌─────────┬───────┬──────────┬──────┬──────────┬─────────────┐
│ Subject │ Group │ Subgroup │ Type │ Language │ Sessions    │
├─────────┼───────┼──────────┼──────┼──────────┼─────────────┤
│ IES     │ 101   │ 111      │ T    │ English  │ Mon 8-10    │
│         │       │          │      │          │ Wed 8-10    │
│ XC      │ 201   │ 211      │ T    │ Spanish  │ Tue 10-12   │
│         │       │          │      │          │ Thu 10-12   │
│         │ 201   │ 221      │ L    │ English  │ Fri 12-14   │
└─────────┴───────┴──────────┴──────┴──────────┴─────────────┘
```

### Navigation Controls

| Key | Action |
|-----|--------|
| `←` / `→` | Navigate between different schedules |
| `Tab` | Toggle between grid view and detailed view |
| `S` | Toggle sorting mode (Groups ↔ Dead Hours) |
| `Space` | Open current schedule URL in web browser |
| `Esc` | Return to main menu |
| `Q` | Quit application |

### Sorting Modes

**Groups Mode:**
- Prioritizes schedules with fewer total groups
- Minimizes number of different professors
- Reduces complexity of course management

**Dead Hours Mode:**
- Prioritizes schedules with fewer gaps between classes
- Optimizes for time efficiency
- Reduces waiting time on campus

## Subject Browser

### Launch Subject Browser

From main menu, select "List subjects" to access the subject browser.

### Quadrimester Selection

**Year Selection:**
```
Select year:
❯ 2024
  2023
  2022
```

**Quadrimester Selection:**
```
Select quadrimester:
❯ Q1 (September - January)
  Q2 (February - June)
```

**Language Selection:**
```
Select display language:
❯ English
  Spanish
  Catalan
```

### Subject List Display

**Interactive Subject Table:**
```
Subjects 156                    2nd quarter of 2024

┌──────┬─────────────────────────────────────────────────────┐
│ Code │ Name                                                │
├──────┼─────────────────────────────────────────────────────┤
│ ASO  │ Advanced Operating Systems                          │
│ BD   │ Databases                                           │
│ IES  │ Software Engineering                                │
│ PROP │ Programming Project                                 │
│ SO   │ Operating Systems                                   │
│ XC   │ Computer Networks                                   │
└──────┴─────────────────────────────────────────────────────┘

ESC to leave    Q to quit
```

**Features:**
- **Alphabetical Sorting**: Subjects sorted by code
- **Multi-language Support**: Names displayed in selected language
- **Quick Navigation**: Scroll through all available subjects
- **Statistics**: Total subject count displayed

## Grade Calculator (Beta)

### Accessing Grade Calculator

Select "Calculate marks" from main menu to enter the grade calculator interface.

### Formula Input Process

**Step 1: Formula Entry**
```
Enter formula (e.g., EX1*0.4+EX2*0.6):
❯ LAB*0.3 + MIDTERM*0.3 + FINAL*0.4

Use variable names for marks
```

**Formula Validation:**
- Real-time syntax checking
- Automatic variable detection
- Error highlighting for invalid formulas

**Step 2: Target Grade**
```
Enter target mark (e.g., 5.0):
❯ 7.0

The minimum mark you want to achieve
```

**Step 3: Known Values**
For each variable detected in the formula:
```
Enter value for LAB (or press Enter to skip):
❯ 8.5

Enter value for MIDTERM (or press Enter to skip):
❯ 6.0

Enter value for FINAL (or press Enter to skip):
❯ [Skip - this is what we want to calculate]
```

### Results Display

**Calculation Results:**
```
Grade Calculation Results

Formula: LAB*0.3 + MIDTERM*0.3 + FINAL*0.4
Target: 7.0

Known Values:
┌─────────┬───────┐
│ Variable│ Value │
├─────────┼───────┤
│ LAB     │ 8.5   │
│ MIDTERM │ 6.0   │
└─────────┴───────┘

Required Values:
┌─────────┬───────────┐
│ Variable│ Required  │
├─────────┼───────────┤
│ FINAL   │ 6.25      │
└─────────┴───────────┘

Result: With FINAL = 6.25, final grade will be 7.0

ESC to leave    Q to quit
```

## Advanced Interactive Features

### Error Handling and Feedback

**User-Friendly Error Messages:**
```
⚠ Warning: No schedules found with current constraints

Suggestions:
• Increase maximum days from 3 to 4
• Expand time range (currently 9-16)
• Remove language restrictions
• Enable subgroup flexibility

Press Enter to modify constraints, Esc to return
```

**Input Validation:**
- Real-time validation of user inputs
- Helpful error messages with suggestions
- Automatic constraint conflict detection

### Progress Indicators

**API Data Loading:**
```
Loading subject data...
[████████████████░░░░] 80% - Fetching class schedules
```

**Schedule Generation:**
```
Generating combinations...
[████████████████████] 100% - Found 24 valid schedules
Processing constraints...
[████████████████████] 100% - Applied filters
```

### Contextual Help

**In-line Instructions:**
- Each interface element includes usage instructions
- Keyboard shortcuts displayed at bottom of screen
- Context-sensitive help based on current operation

**Example Help Text:**
```
(Use ↑↓ and Enter)
(Use ↑↓, Space to toggle, Enter to confirm)
(Type to filter, use ↑↓ for navigation)
```

## Integration with External Systems

### Browser Integration

**Automatic URL Opening:**
When viewing a schedule, press `Space` to:
1. Generate official UPC schedule URL
2. Open URL in default web browser
3. Navigate directly to enrollment interface
4. Pre-fill schedule selection when possible

**URL Format:**
```
https://raco.fib.upc.edu/manage/schedule/
?subjects=IES,XC&groups=101,201&subgroups=111,211
```

### Data Export Capabilities

While in interactive mode, all data can be exported:
- **Schedule Data**: Complete JSON export of current results
- **Subject Lists**: Multi-language subject catalogs
- **Grade Calculations**: Detailed calculation breakdowns

## Customization and Preferences

### Display Preferences

**Color Themes:**
- Automatic detection of terminal color support
- Graceful degradation for limited color terminals
- High contrast mode for accessibility

**Layout Options:**
- Adaptive table widths based on terminal size
- Responsive design for different screen sizes
- Compact mode for smaller terminals

### Keyboard Shortcuts

**Global Shortcuts:**
- `Q`: Quick quit from any screen
- `Esc`: Go back/cancel current operation
- `Ctrl+C`: Emergency exit (force quit)

**Context-Specific Shortcuts:**
- `Tab`: Toggle between different views
- `Space`: Action button (varies by context)
- `S`: Sort/settings toggle
- `Enter`: Confirm/select

## Performance and Responsiveness

### Optimization Features

**Smart Caching:**
- Session-based API response caching
- Reduced loading times for repeated operations
- Intelligent cache invalidation

**Progressive Loading:**
- Display partial results while processing continues
- Real-time progress updates
- Cancellable long-running operations

**Memory Management:**
- Efficient data structures for large result sets
- Garbage collection between operations
- Memory usage monitoring

### User Experience Enhancements

**Responsive Design:**
- Automatic adaptation to terminal size
- Optimized layouts for different screen dimensions
- Graceful handling of window resizing

**Accessibility Features:**
- High contrast mode support
- Screen reader friendly output
- Alternative input methods for limited environments

## Tips for Effective Usage

### Best Practices

1. **Start Broad, Narrow Down:**
   - Begin with minimal constraints
   - Gradually add restrictions based on results
   - Use iteration to find optimal schedules

2. **Use Visual Feedback:**
   - Pay attention to color coding in schedules
   - Review statistics (dead hours, group counts)
   - Compare different sorting modes

3. **Leverage Browser Integration:**
   - Use `Space` to open promising schedules
   - Compare multiple options in browser tabs
   - Bookmark favorites for later reference

### Common Workflows

**Schedule Planning Workflow:**
1. Browse subjects to understand options
2. Select core required subjects first
3. Add electives based on availability
4. Refine constraints iteratively
5. Compare top options in browser

**Grade Planning Workflow:**
1. Input complex course formula
2. Enter known grades progressively
3. Calculate requirements for remaining exams
4. Explore different scenarios
5. Plan study priorities accordingly

### Troubleshooting Interactive Issues

**Display Problems:**
- Ensure terminal supports ANSI colors
- Try different terminal applications
- Check terminal size (minimum 80x24 recommended)

**Navigation Issues:**
- Verify keyboard input is working
- Check for conflicting key bindings
- Try alternative navigation keys

**Performance Issues:**
- Reduce number of subjects in complex searches
- Add constraints to limit combinations
- Close other resource-intensive applications

## Future Interactive Features

### Planned Enhancements

1. **Enhanced Visualizations:**
   - Graphical schedule representation
   - Conflict visualization
   - Time distribution charts

2. **Smart Recommendations:**
   - AI-powered schedule suggestions
   - Learning from user preferences
   - Automatic constraint optimization

3. **Extended Integration:**
   - Calendar application export
   - Mobile companion app
   - Social features for schedule sharing

4. **Advanced Customization:**
   - User-defined themes
   - Custom keyboard shortcuts
   - Personalized interface layouts

The interactive mode of FIB Manager provides a comprehensive, user-friendly interface that guides users through complex academic planning tasks while maintaining the power and flexibility of the underlying system.
