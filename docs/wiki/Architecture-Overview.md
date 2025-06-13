# Architecture Overview

This document provides a comprehensive overview of FIB Manager's system architecture, design patterns, and component interactions.

## System Architecture

FIB Manager follows a modular, layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                     │
├─────────────────────────┬───────────────────────────────────┤
│    CLI Commands         │      Interactive UI               │
│    (command_line.py)    │      (interactive.py, ui.py)      │
└─────────────────────────┴───────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                     │
├──────────────┬──────────────┬─────────────┬─────────────────┤
│   Search     │   Subjects   │    Marks    │   Core Utils    │
│ (search.py)  │(subjects.py) │ (marks.py)  │   (core/*)      │
└──────────────┴──────────────┴─────────────┴─────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                    Data Access Layer                        │
├─────────────────────────┬───────────────────────────────────┤
│       API Client        │        Data Processing           │
│       (api.py)          │    (parser.py, validator.py)     │
└─────────────────────────┴───────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                    External Services                        │
├─────────────────────────┬───────────────────────────────────┤
│      UPC API            │       System Resources           │
│ (raco.fib.upc.edu)      │   (Filesystem, Network, etc.)    │
└─────────────────────────┴───────────────────────────────────┘
```

## Core Components

### 1. Entry Points

**Main Entry Point (`__main__.py`)**
- Application bootstrap for compiled executables
- Imports and delegates to command-line interface
- Handles top-level exception management

**Command Line Interface (`commands/command_line.py`)**
- Argument parsing and validation
- Command routing and delegation
- Global configuration and error handling

### 2. User Interface Components

**Interactive Mode (`ui/interactive.py`)**
- Menu-driven interface with keyboard navigation
- User input collection and validation
- Integration with visual display components

**UI Rendering (`ui/ui.py`)**
- Rich terminal output formatting
- Table and grid rendering
- Color-coded schedule visualization
- Progress indicators and user feedback

### 3. Business Logic

**Schedule Search (`commands/search.py`)**
- Schedule generation orchestration
- Filtering and sorting logic
- Result formatting and output

**Subject Management (`commands/subjects.py`)**
- Subject listing and browsing
- Multi-language name resolution
- Interactive subject selection

**Grade Calculator (`commands/marks.py`)**
- Mathematical formula parsing
- Variable solving algorithms
- Safe expression evaluation

### 4. Core Services

**Schedule Generator (`core/schedule_generator.py`)**
- Combination generation algorithms
- Constraint satisfaction logic
- Performance optimization

**Data Parser (`core/parser.py`)**
- API response processing
- Data normalization and transformation
- Schedule data structure creation

**Validator (`core/validator.py`)**
- Schedule validation rules
- Conflict detection
- Dead hours calculation

**Utilities (`core/utils.py`)**
- Common helper functions
- Terminal management
- Language normalization

### 5. Data Access

**API Client (`api/api.py`)**
- HTTP request management
- Response caching
- Error handling and retry logic

**Constants (`core/constants.py`)**
- Configuration parameters
- API endpoints and mappings
- Application settings

## Design Patterns

### 1. Command Pattern
Each CLI command is implemented as a separate module with a consistent interface:

```python
def add_[command]_arguments(parser: ArgumentParser, default_quad: str) -> None:
    """Add command-specific arguments to parser"""

def handle_[command]_command(args: Namespace) -> None:
    """Execute the command with parsed arguments"""
```

### 2. Factory Pattern
The argument parser factory creates configured parsers for each command:

```python
def build_argument_parser(default_quad: str) -> ArgumentParser:
    """Build and configure the main argument parser"""
```

### 3. Strategy Pattern
Different output strategies based on user preferences:
- JSON output for programmatic use
- Interactive UI for human interaction
- Rich terminal formatting for readability

### 4. Observer Pattern
UI components respond to user input events:
- Keyboard navigation handlers
- Menu selection callbacks
- Real-time display updates

## Data Flow

### 1. Schedule Generation Flow

```
User Input → Command Parser → Search Controller → API Client
     ↓             ↓               ↓              ↓
Validation → Arguments → Business Logic → UPC API
     ↓             ↓               ↓              ↓
Error Check → Processing → Data Parser → Raw Data
     ↓             ↓               ↓              ↓
Continue → Schedule Generator → Validator → Parsed Data
     ↓             ↓               ↓              ↓
Output Format → Result Formatter → Display → Schedules
```

### 2. Interactive Mode Flow

```
App Launch → Splash Screen → Main Menu → User Choice
     ↓             ↓             ↓           ↓
Initialize → Display → Menu Handler → Action Router
     ↓             ↓             ↓           ↓
Setup UI → Rich Output → Input Capture → Command Execution
     ↓             ↓             ↓           ↓
Navigation → Visual Feedback → Processing → Result Display
```

## Module Dependencies

### Dependency Graph

```
command_line.py
├── search.py
│   ├── core/schedule_generator.py
│   ├── core/parser.py
│   ├── core/validator.py
│   ├── api/api.py
│   └── ui/ui.py
├── subjects.py
│   ├── core/parser.py
│   ├── api/api.py
│   └── ui/ui.py
├── marks.py
│   └── ui/ui.py
├── ui/interactive.py
│   ├── ui/ui.py
│   ├── api/api.py
│   └── core/parser.py
└── core/utils.py
```

### Key Interfaces

**API Interface (`api/api.py`)**
```python
def fetch_classes_data(quad: str, lang: str) -> Dict[str, Any]
def fetch_subject_names(lang: str) -> Dict[str, str]
def get_paginated_data(base_url: str, lang: str) -> List[Dict[str, Any]]
```

**Parser Interface (`core/parser.py`)**
```python
def parse_classes_data(raw_data: Dict[str, Any]) -> Dict[str, Any]
def split_schedule_by_group_type(parsed_data: dict) -> Tuple[dict, dict]
```

**UI Interface (`ui/ui.py`)**
```python
def display_interface_schedule(...) -> None
def navigate_schedules(...) -> None
def display_subjects_list(...) -> None
```

## Error Handling Strategy

### 1. Layered Error Handling

**Application Layer:**
- User-friendly error messages
- Graceful degradation
- Alternative workflows

**Business Logic Layer:**
- Input validation
- Constraint checking
- Business rule enforcement

**Data Access Layer:**
- Network error handling
- API response validation
- Retry mechanisms

### 2. Error Types

**User Errors:**
- Invalid input parameters
- Missing required arguments
- Malformed formulas

**System Errors:**
- Network connectivity issues
- API service unavailability
- Insufficient system resources

**Data Errors:**
- Corrupt API responses
- Missing or invalid data
- Parsing failures

## Configuration Management

### 1. Configuration Sources

1. **Command-line Arguments** (highest priority)
2. **Environment Variables**
3. **Application Constants** (lowest priority)

### 2. Configuration Categories

**API Configuration:**
- Base URLs and endpoints
- Request timeouts and retries
- Authentication parameters

**UI Configuration:**
- Color schemes and themes
- Display preferences
- Keyboard mappings

**Performance Configuration:**
- Cache settings
- Batch sizes
- Memory limits

## Security Considerations

### 1. Input Validation
- All user inputs are validated before processing
- Mathematical formulas use safe evaluation
- File paths are sanitized

### 2. API Security
- HTTPS for all API communications
- No sensitive data in logs
- Proper error message sanitization

### 3. Formula Evaluation
- Restricted function whitelist
- No arbitrary code execution
- Mathematical operations only

## Performance Architecture

### 1. Caching Strategy
- In-memory API response caching
- Session-based data persistence
- Intelligent cache invalidation

### 2. Optimization Techniques
- Lazy loading of heavy resources
- Parallel API requests where possible
- Efficient data structures

### 3. Resource Management
- Memory-conscious data processing
- Graceful handling of large datasets
- Proper cleanup of system resources

## Testing Architecture

### 1. Unit Testing
- Individual component testing
- Mock API responses
- Edge case validation

### 2. Integration Testing
- Component interaction testing
- End-to-end workflow validation
- API integration verification

### 3. User Interface Testing
- Interactive flow testing
- Keyboard navigation validation
- Display output verification

## Extensibility Points

### 1. Command System
- Easy addition of new commands
- Consistent argument handling
- Shared infrastructure

### 2. Output Formats
- Pluggable output formatters
- Multiple display options
- Custom rendering support

### 3. Data Sources
- Modular API client design
- Configurable endpoints
- Alternative data providers

## Deployment Architecture

### 1. Development Environment
- Virtual environment isolation
- Development dependencies
- Debug configuration

### 2. Distribution Packages
- PyInstaller executable generation
- Dependency bundling
- Cross-platform compatibility

### 3. Production Considerations
- Error logging and monitoring
- Performance metrics
- Update mechanisms
