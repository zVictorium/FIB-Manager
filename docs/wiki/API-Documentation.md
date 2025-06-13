# API Documentation

Complete documentation for FIB Manager's integration with the UPC API and internal data handling systems.

## UPC API Overview

FIB Manager integrates with the official UPC (Universitat Politècnica de Catalunya) API to fetch real-time academic data. The API provides access to:

- Class schedules and timetables
- Subject information and metadata
- Group and subgroup assignments
- Multi-language subject names
- Academic calendar data

### Base Configuration

**API Base URL:** `https://raco.fib.upc.edu/api/`  
**Client ID:** `fib-manager`  
**Supported Languages:** `en` (English), `es` (Spanish), `ca` (Catalan)  
**Response Format:** JSON  
**Authentication:** None required (public API)

## API Client Implementation

### Core Functions

#### `fetch_classes_data(quad: str, lang: str) -> Dict[str, Any]`

Fetches complete class schedule data for a specific quadrimester.

**Parameters:**
- `quad` (str): Quadrimester code (e.g., "2024Q1")
- `lang` (str): Language code ("en", "es", "ca")

**Returns:**
- Dictionary containing raw API response with class data

**Example Response:**
```json
{
  "results": [
    {
      "codi_assig": "IES",
      "nom": "Software Engineering",
      "grup": "101",
      "subgrup": "111",
      "tipus": "Teoria",
      "inici": "08:00",
      "final": "10:00",
      "dia_setmana": "Dl",
      "idioma": "Anglès"
    }
  ],
  "next": null,
  "count": 1
}
```

**Usage:**
```python
from app.api import fetch_classes_data

# Fetch English class data for 2024Q1
data = fetch_classes_data("2024Q1", "en")
classes = data.get("results", [])
```

#### `fetch_subject_names(lang: str) -> Dict[str, str]`

Retrieves human-readable subject names in the specified language.

**Parameters:**
- `lang` (str): Language code ("en", "es", "ca")

**Returns:**
- Dictionary mapping subject codes to names

**Example Response:**
```json
{
  "IES": "Software Engineering",
  "XC": "Computer Networks", 
  "PROP": "Programming Project",
  "BD": "Databases"
}
```

**Usage:**
```python
from app.api import fetch_subject_names

# Get English subject names
names = fetch_subject_names("en")
subject_name = names.get("IES", "IES")  # "Software Engineering"
```

### Utility Functions

#### `get_json_response(url: str, language: str) -> Dict[str, Any]`

Low-level function for making HTTP requests to the API.

**Parameters:**
- `url` (str): Complete API endpoint URL
- `language` (str): Language code for Accept-Language header

**Returns:**
- JSON response as dictionary

**Error Handling:**
- Returns `{"results": []}` on HTTP errors
- Logs error details for debugging
- Handles network timeouts gracefully

#### `get_paginated_data(base_url: str, language: str) -> List[Dict[str, Any]]`

Fetches all pages of data from paginated API endpoints.

**Parameters:**
- `base_url` (str): Base API endpoint URL
- `language` (str): Language code

**Returns:**
- List of all results from all pages

**Implementation Details:**
- Follows `next` links automatically
- Aggregates results from multiple pages
- Handles pagination errors gracefully

## Data Models

### Raw API Data Structure

The UPC API returns class data with these fields:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `codi_assig` | String | Subject code | "IES" |
| `nom` | String | Subject name (localized) | "Software Engineering" |
| `grup` | String | Group number | "101" |
| `subgrup` | String | Subgroup number | "111" |
| `tipus` | String | Class type (localized) | "Teoria" |
| `inici` | String | Start time (HH:MM) | "08:00" |
| `final` | String | End time (HH:MM) | "10:00" |
| `dia_setmana` | String | Day of week (localized) | "Dl" |
| `idioma` | String | Language (localized) | "Anglès" |

### Parsed Data Structure

FIB Manager transforms raw API data into structured format:

```python
{
  "IES": {  # Subject code
    "101": {  # Group number
      "111": [  # Subgroup number
        {
          "subject": "IES",
          "group": 101,
          "subgroup": 111,
          "type": "T",  # Normalized type
          "start_hour": 8,
          "end_hour": 10,
          "day": 1,  # Monday = 1
          "language": "en"
        }
      ]
    }
  }
}
```

## Language Support

### Language Mapping

FIB Manager normalizes language codes between user input and API requirements:

| User Input | API Code | Display Name |
|------------|----------|--------------|
| `en` | `en` | English |
| `es` | `es` | Spanish |
| `ca` | `ca` | Catalan |

### Localized Field Values

The API returns localized values that need normalization:

**Day Names:**
- English: "Monday", "Tuesday", etc.
- Spanish: "Lunes", "Martes", etc.
- Catalan: "Dilluns", "Dimarts", etc.

**Class Types:**
- English: "Theory", "Laboratory", "Problems"
- Spanish: "Teoría", "Laboratorio", "Problemas"
- Catalan: "Teoria", "Laboratori", "Problemes"

**Languages:**
- English: "English", "Spanish", "Catalan"
- Spanish: "Inglés", "Español", "Catalán"
- Catalan: "Anglès", "Espanyol", "Català"

## Error Handling

### HTTP Status Codes

| Code | Description | FIB Manager Action |
|------|-------------|-------------------|
| 200 | Success | Process response normally |
| 400 | Bad Request | Log error, return empty results |
| 404 | Not Found | Log error, return empty results |
| 500 | Server Error | Log error, return empty results |
| Timeout | Network timeout | Log error, return empty results |

### Error Response Format

When errors occur, the API client returns:

```python
{
  "results": [],
  "error": "HTTP 500",
  "message": "Failed to fetch data"
}
```

### Logging

API errors are logged with these details:
- HTTP status code
- Request URL
- Response headers
- Error message
- Timestamp

Example log entry:
```
2024-06-13 10:30:15 ERROR Failed to fetch data: HTTP 500 for URL: https://raco.fib.upc.edu/api/classes/2024Q1
```

## Caching Strategy

### Response Caching

FIB Manager implements session-based caching to improve performance:

**Cache Key Format:** `{endpoint}_{language}_{quadrimester}`  
**Cache Duration:** Session-based (memory only)  
**Cache Invalidation:** Automatic on application restart

**Benefits:**
- Reduced API calls during single session
- Faster response times for repeated queries
- Lower server load

**Implementation:**
```python
# Pseudo-code for caching
cache = {}
cache_key = f"classes_{lang}_{quad}"

if cache_key in cache:
    return cache[cache_key]
else:
    data = make_api_request(url)
    cache[cache_key] = data
    return data
```

## Rate Limiting

### API Limits

The UPC API doesn't enforce strict rate limits, but FIB Manager implements responsible usage:

- **Maximum concurrent requests:** 3
- **Request delay:** 100ms between requests
- **Retry attempts:** 3 with exponential backoff
- **Timeout:** 10 seconds per request

### Best Practices

1. **Cache responses** to minimize API calls
2. **Batch related requests** when possible  
3. **Use specific quadrimester codes** instead of auto-detection
4. **Implement proper error handling** for graceful degradation

## Data Validation

### Input Validation

Before making API requests, FIB Manager validates:

**Quadrimester Format:**
- Pattern: `YYYYQ[1-2]`
- Examples: "2024Q1", "2023Q2"
- Validation: Year ≥ 2020, Quarter ∈ {1, 2}

**Language Codes:**
- Allowed values: ["en", "es", "ca"]
- Default fallback: "en"
- Case insensitive input

**Subject Codes:**
- Pattern: `[A-Z]{2,6}`
- Examples: "IES", "XC", "PROP"
- Uppercase normalization

### Response Validation

API responses are validated for:

1. **Required Fields:** Presence of essential data fields
2. **Data Types:** Correct field types and formats
3. **Value Ranges:** Reasonable time ranges and numeric values
4. **Consistency:** Cross-field validation rules

**Example Validation:**
```python
def validate_class_data(class_item):
    required_fields = ['codi_assig', 'grup', 'subgrup', 'inici', 'final']
    
    for field in required_fields:
        if field not in class_item:
            raise ValidationError(f"Missing required field: {field}")
    
    # Validate time format
    start_time = parse_time(class_item['inici'])
    end_time = parse_time(class_item['final'])
    
    if start_time >= end_time:
        raise ValidationError("Invalid time range")
```

## API Testing

### Test Data

FIB Manager includes test fixtures for API development:

**Mock Responses:**
```python
MOCK_CLASSES_RESPONSE = {
    "results": [
        {
            "codi_assig": "TEST",
            "nom": "Test Subject",
            "grup": "101",
            "subgrup": "111",
            "tipus": "Teoria",
            "inici": "08:00",
            "final": "10:00",
            "dia_setmana": "Dl",
            "idioma": "Anglès"
        }
    ],
    "next": None,
    "count": 1
}
```

### Integration Testing

**API Health Check:**
```bash
# Test API connectivity
fib-manager subjects --quadrimester 2024Q1
```

**Response Validation:**
```python
def test_api_response():
    data = fetch_classes_data("2024Q1", "en")
    assert "results" in data
    assert isinstance(data["results"], list)
```

## Troubleshooting

### Common Issues

**"Failed to fetch data: HTTP 500"**
- Cause: UPC API server error
- Solution: Retry request, check API status
- Workaround: Use cached data if available

**"Connection timeout"**
- Cause: Network connectivity issues
- Solution: Check internet connection
- Workaround: Increase timeout value

**"Invalid quadrimester format"**
- Cause: Malformed quadrimester code
- Solution: Use format YYYYQ[1-2]
- Example: "2024Q1" not "24Q1"

**"Subject not found: XYZ"**
- Cause: Subject code doesn't exist in quadrimester
- Solution: Verify subject code and quadrimester
- Use: `fib-manager subjects` to list available subjects

### Debug Mode

Enable debug logging for API troubleshooting:

```bash
# Windows
set FIB_DEBUG=true
fib-manager subjects

# Linux/macOS
export FIB_DEBUG=true
fib-manager subjects
```

Debug output includes:
- API request URLs
- Response status codes
- Response headers
- Timing information
- Error details

## Future Enhancements

### Planned Improvements

1. **Persistent Caching:** File-based cache for cross-session persistence
2. **Background Updates:** Automatic cache refresh for updated data
3. **API Versioning:** Support for multiple API versions
4. **Enhanced Error Recovery:** Intelligent retry strategies
5. **Performance Metrics:** Request timing and success rate tracking

### API Extensions

Potential future API integrations:
- Student grades and transcripts
- Course prerequisites and descriptions
- Professor information and ratings
- Classroom locations and capacity
- Academic calendar events
