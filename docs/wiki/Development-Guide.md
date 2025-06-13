# Development Guide

Comprehensive guide for developers who want to contribute to FIB Manager or understand its development workflow.

## Development Environment Setup

### Prerequisites

Before starting development, ensure you have:

- **Python 3.8+** with pip and venv
- **Git** for version control
- **Modern terminal** with ANSI color support
- **Code editor** (VS Code, PyCharm, vim, etc.)
- **Internet connection** for API testing

### Quick Development Setup

#### Windows

```cmd
# Clone the repository
git clone https://github.com/zvictorium/fib-manager.git
cd fib-manager

# Run automated setup
.\scripts\setup.bat

# Activate development environment
.venv\Scripts\activate

# Verify setup
fib-manager --help
python -m pytest  # If tests are available
```

#### macOS/Linux

```bash
# Clone the repository
git clone https://github.com/zvictorium/fib-manager.git
cd fib-manager

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Install development dependencies (if available)
pip install -r requirements-dev.txt  # If exists

# Verify setup
fib-manager --help
```

### Manual Development Setup

For full control over the development environment:

```bash
# 1. Create and activate virtual environment
python3 -m venv fib-dev-env
source fib-dev-env/bin/activate  # Windows: fib-dev-env\Scripts\activate

# 2. Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# 3. Install project in editable mode
pip install -e .

# 4. Install development tools
pip install black flake8 mypy pytest pytest-cov

# 5. Set up git hooks (optional)
git config core.hooksPath .githooks
```

## Project Structure Deep Dive

### Directory Layout

```
fib-manager/
├── src/app/                    # Main application source
│   ├── __init__.py            # Package initialization
│   ├── __main__.py            # Entry point for -m execution
│   ├── __version__.py         # Version information
│   ├── api/                   # API integration layer
│   │   ├── __init__.py        # API exports
│   │   └── api.py             # UPC API client implementation
│   ├── commands/              # CLI command implementations
│   │   ├── __init__.py        # Commands package
│   │   ├── command_line.py    # Main CLI entry and argument parsing
│   │   ├── search.py          # Schedule search logic
│   │   ├── subjects.py        # Subject listing functionality
│   │   └── marks.py           # Grade calculator (Beta)
│   ├── core/                  # Core business logic
│   │   ├── __init__.py        # Core package
│   │   ├── constants.py       # Application constants
│   │   ├── parser.py          # Data parsing utilities
│   │   ├── schedule_generator.py # Schedule generation engine
│   │   ├── utils.py           # Common utilities
│   │   └── validator.py       # Validation and filtering logic
│   └── ui/                    # User interface components
│       ├── __init__.py        # UI package
│       ├── interactive.py     # Interactive mode implementation
│       └── ui.py              # Display and rendering utilities
├── scripts/                   # Build and utility scripts
│   ├── setup.bat             # Windows development setup
│   ├── start.bat             # Windows launcher script
│   └── compile.bat           # PyInstaller build script
├── docs/                     # Documentation
│   ├── screenshots/          # Application screenshots
│   └── wiki/                # Wiki documentation (this directory)
├── tests/                    # Test suite (if exists)
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_parser.py
│   └── test_cli.py
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Development dependencies (if exists)
├── setup.py                  # Package configuration
├── README.md                 # User documentation
├── LICENSE                   # License file
└── .gitignore               # Git ignore patterns
```

### Key Files and Their Purposes

**Entry Points:**
- `src/app/__main__.py`: Python module entry (`python -m app`)
- `src/app/commands/command_line.py`: CLI entry point and routing

**Core Logic:**
- `src/app/core/schedule_generator.py`: Main algorithm implementation
- `src/app/core/validator.py`: Schedule validation and constraint checking
- `src/app/core/parser.py`: API data transformation

**User Interface:**
- `src/app/ui/interactive.py`: Menu-driven interface
- `src/app/ui/ui.py`: Rich terminal output and visual components

**External Integration:**
- `src/app/api/api.py`: UPC API client with caching and error handling

## Code Style and Standards

### Python Style Guidelines

FIB Manager follows these coding standards:

**PEP 8 Compliance:**
- Line length: 120 characters maximum
- 4 spaces for indentation (no tabs)
- Snake_case for functions and variables
- PascalCase for classes
- UPPERCASE for constants

**Type Hints:**
```python
# Always include type hints for function parameters and return values
def fetch_classes_data(quad: str, lang: str) -> Dict[str, Any]:
    """Fetch class data from API."""
    pass

# Use Union for multiple types, Optional for nullable
from typing import Dict, List, Optional, Union

def process_subjects(subjects: List[str], lang: Optional[str] = None) -> Dict[str, str]:
    """Process subject list with optional language."""
    pass
```

**Docstring Format:**
```python
def complex_function(param1: str, param2: int, param3: bool = False) -> List[Dict[str, Any]]:
    """
    Brief description of function purpose.
    
    Detailed explanation of what the function does, including any important
    side effects or behavior notes.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter  
        param3: Description of optional parameter (default: False)
    
    Returns:
        List of dictionaries containing processed data
        
    Raises:
        ValueError: When param1 is empty or invalid
        ApiError: When API request fails
        
    Example:
        >>> result = complex_function("test", 42, True)
        >>> len(result)
        3
    """
    pass
```

### Code Organization Patterns

**Import Organization:**
```python
# 1. Standard library imports
import os
import sys
from typing import Dict, List, Any

# 2. Third-party imports
import requests
from rich.console import Console

# 3. Local application imports
from app.core.constants import API_BASE_URL
from app.core.utils import normalize_language
```

**Error Handling Pattern:**
```python
def api_function() -> Dict[str, Any]:
    """Standard error handling pattern."""
    try:
        response = make_request()
        return process_response(response)
    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        return {"results": [], "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
```

**Configuration Pattern:**
```python
# Use constants module for configuration
from app.core.constants import DEFAULT_TIMEOUT, MAX_RETRIES

# Support environment variable overrides
import os
timeout = int(os.getenv('FIB_TIMEOUT', DEFAULT_TIMEOUT))
```

## Testing Guidelines

### Test Structure

```python
# tests/test_module.py
import pytest
from unittest.mock import Mock, patch

from app.module import function_to_test

class TestFunctionToTest:
    """Test suite for function_to_test."""
    
    def test_basic_functionality(self):
        """Test basic functionality with valid input."""
        result = function_to_test("valid_input")
        assert result is not None
        assert isinstance(result, dict)
    
    def test_error_handling(self):
        """Test error handling with invalid input."""
        with pytest.raises(ValueError):
            function_to_test("")
    
    @patch('app.module.external_dependency')
    def test_with_mock(self, mock_dependency):
        """Test with mocked external dependency."""
        mock_dependency.return_value = {"test": "data"}
        result = function_to_test("input")
        assert result["test"] == "data"
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app

# Run specific test file
python -m pytest tests/test_api.py

# Run with verbose output
python -m pytest -v

# Run tests matching pattern
python -m pytest -k "test_api"
```

### Test Categories

**Unit Tests:**
- Test individual functions in isolation
- Mock external dependencies
- Focus on business logic validation

**Integration Tests:**
- Test component interactions
- Use real API calls (with careful rate limiting)
- Validate end-to-end workflows

**CLI Tests:**
- Test command-line interface
- Validate argument parsing
- Check output formats

## Debugging and Development Tools

### Logging Configuration

```python
# Development logging setup
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fib-manager-debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Debug Mode

Enable debug mode for development:

```bash
# Enable debug logging
export FIB_DEBUG=true

# Run with debug output
fib-manager subjects
```

### Interactive Debugging

```python
# Add breakpoints for debugging
import pdb; pdb.set_trace()

# Or use ipdb for enhanced debugging
import ipdb; ipdb.set_trace()

# Use in exception handlers
try:
    risky_function()
except Exception as e:
    import pdb; pdb.set_trace()
    raise
```

### Performance Profiling

```python
# Profile function execution
import cProfile
import pstats

def profile_function():
    """Profile a specific function."""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Your code here
    result = expensive_function()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions
    
    return result
```

## Build and Release Process

### Development Build

```bash
# Install in development mode (changes take effect immediately)
pip install -e .

# Test changes
fib-manager --help
```

### Creating Executables

Use the provided build script:

```bash
# Windows
.\scripts\compile.bat

# The script will:
# 1. Create virtual environment
# 2. Install dependencies
# 3. Run PyInstaller
# 4. Generate executables in dist/
```

### Manual PyInstaller Build

```bash
# Install PyInstaller
pip install pyinstaller

# Create CLI executable
pyinstaller --onefile \
    --name fib-manager \
    --paths src \
    src/app/__main__.py

# Create GUI executable (for interactive mode)
pyinstaller --onefile \
    --name "FIB Manager" \
    --console \
    --paths src \
    src/app/__main__.py
```

### Release Checklist

Before creating a release:

1. **Update Version:**
   ```python
   # src/app/__version__.py
   __version__ = "1.2.0"
   ```

2. **Update Documentation:**
   - README.md
   - CHANGELOG.md
   - Wiki pages if necessary

3. **Run Tests:**
   ```bash
   python -m pytest
   flake8 src/
   mypy src/
   ```

4. **Build Executables:**
   ```bash
   .\scripts\compile.bat  # Windows
   # Or manual build for other platforms
   ```

5. **Test Executables:**
   ```bash
   dist/fib-manager.exe --help
   dist/"FIB Manager.exe"
   ```

6. **Create Git Tag:**
   ```bash
   git tag -a v1.2.0 -m "Release version 1.2.0"
   git push origin v1.2.0
   ```

## Contributing Guidelines

### Git Workflow

**Branch Naming:**
- `feature/description` - New features
- `bugfix/issue-number` - Bug fixes
- `hotfix/critical-issue` - Critical fixes
- `docs/improvement` - Documentation updates

**Commit Messages:**
```
type(scope): description

- feat: new feature
- fix: bug fix
- docs: documentation changes
- style: formatting changes
- refactor: code refactoring
- test: test additions/changes
- chore: maintenance tasks

Examples:
feat(api): add caching support for API responses
fix(cli): handle empty subject list gracefully
docs(wiki): update installation guide for macOS
```

### Pull Request Process

1. **Create Feature Branch:**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make Changes:**
   - Write code following style guidelines
   - Add tests for new functionality
   - Update documentation

3. **Test Changes:**
   ```bash
   python -m pytest
   fib-manager --help  # Smoke test
   ```

4. **Commit Changes:**
   ```bash
   git add .
   git commit -m "feat(core): add new schedule filtering option"
   ```

5. **Push and Create PR:**
   ```bash
   git push origin feature/my-new-feature
   # Create pull request on GitHub
   ```

### Code Review Standards

**What Reviewers Look For:**

1. **Functionality:**
   - Does the code solve the intended problem?
   - Are edge cases handled properly?
   - Is error handling appropriate?

2. **Code Quality:**
   - Follows coding standards and style guide
   - Has appropriate documentation and comments
   - Includes tests for new functionality

3. **Performance:**
   - No obvious performance issues
   - Efficient algorithms and data structures
   - Appropriate use of caching

4. **Maintainability:**
   - Code is readable and well-organized
   - Uses consistent patterns
   - Avoids unnecessary complexity

## Advanced Development Topics

### Adding New Commands

To add a new CLI command:

1. **Create Command Module:**
   ```python
   # src/app/commands/new_command.py
   from argparse import ArgumentParser, Namespace
   
   def add_new_command_arguments(parser: ArgumentParser, default_quad: str) -> None:
       """Add arguments for new command."""
       parser.add_argument("--option", help="Command option")
   
   def handle_new_command_command(args: Namespace) -> None:
       """Handle the new command."""
       print(f"Executing new command with option: {args.option}")
   ```

2. **Register Command:**
   ```python
   # src/app/commands/command_line.py
   from app.commands.new_command import add_new_command_arguments, handle_new_command_command
   
   def build_argument_parser(default_quad: str) -> ArgumentParser:
       # ... existing code ...
       
       # Add new command
       new_parser = subparsers.add_parser("new-command", help="Description")
       add_new_command_arguments(new_parser, default_quad)
       
       return parser
   
   def main() -> None:
       # ... existing code ...
       elif args.command == "new-command":
           handle_new_command_command(args)
   ```

### Extending the API

To add support for new API endpoints:

1. **Add Constants:**
   ```python
   # src/app/core/constants.py
   NEW_ENDPOINT = "new-data"
   ```

2. **Implement API Function:**
   ```python
   # src/app/api/api.py
   def fetch_new_data(param: str) -> Dict[str, Any]:
       """Fetch new data from API."""
       url = f"{API_BASE_URL}{NEW_ENDPOINT}/?param={param}"
       return get_json_response(url, "en")
   ```

3. **Add Parser Support:**
   ```python
   # src/app/core/parser.py
   def parse_new_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
       """Parse new data format."""
       return {item["id"]: item for item in raw_data.get("results", [])}
   ```

### Custom UI Components

To create new UI components:

```python
# src/app/ui/ui.py
from rich.table import Table
from rich.text import Text

def create_custom_table(data: List[Dict[str, Any]]) -> Table:
    """Create a custom formatted table."""
    table = Table(title="Custom Data View")
    table.add_column("Column 1", style="cyan")
    table.add_column("Column 2", style="magenta")
    
    for item in data:
        table.add_row(str(item["field1"]), str(item["field2"]))
    
    return table
```

## Troubleshooting Development Issues

### Common Development Problems

**Import Errors:**
```bash
# Ensure package is installed in development mode
pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"

# Verify package installation
pip list | grep fib-manager
```

**Test Failures:**
```bash
# Run tests with verbose output
python -m pytest -v --tb=short

# Run single test for debugging
python -m pytest tests/test_specific.py::test_function -s
```

**Build Issues:**
```bash
# Clean previous builds
rm -rf build/ dist/ *.spec

# Verify dependencies
pip install -r requirements.txt

# Check PyInstaller version
pyinstaller --version
```

**API Connection Issues:**
```bash
# Test API manually
curl -I https://raco.fib.upc.edu/api/

# Check DNS resolution
nslookup raco.fib.upc.edu

# Test with debug logging
export FIB_DEBUG=true
python -c "from app.api import fetch_classes_data; print(fetch_classes_data('2024Q1', 'en'))"
```

### Development Environment Issues

**Virtual Environment Problems:**
```bash
# Recreate virtual environment
deactivate
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

**Package Version Conflicts:**
```bash
# Check for conflicts
pip check

# Show package dependencies
pip show package-name

# Create fresh environment for testing
python -m venv test-env
source test-env/bin/activate
pip install -e .
```

## Getting Help

### Development Support

1. **Documentation:** Read through wiki pages and code comments
2. **Code Examples:** Look at existing command implementations
3. **Issue Tracker:** Search for similar development questions
4. **Community:** Discuss development questions in GitHub discussions

### Reporting Development Issues

When reporting development-related issues:

1. **Environment Information:**
   - Python version and OS
   - Virtual environment setup
   - Installed package versions (`pip freeze`)

2. **Error Details:**
   - Complete error messages and stack traces
   - Steps to reproduce
   - Expected vs actual behavior

3. **Code Context:**
   - Relevant code snippets
   - Git commit hash
   - Branch information

### Contributing Back

Ways to contribute to FIB Manager:

1. **Bug Reports:** Detailed issue reports with reproduction steps
2. **Feature Requests:** Well-defined enhancement proposals
3. **Code Contributions:** Pull requests with new features or fixes
4. **Documentation:** Improvements to guides and examples
5. **Testing:** Additional test cases and coverage improvements
6. **User Feedback:** Real-world usage experiences and suggestions
