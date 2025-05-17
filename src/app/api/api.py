"""
API interaction module for fetching data from the FIB API.
"""

import logging
import requests
from typing import Dict, List, Any

from app.core.constants import API_BASE_URL, CLIENT_ID, LANGUAGE_MAPPING, DEFAULT_LANGUAGE

# Initialize module logger
logger = logging.getLogger(__name__)

def get_json_response(url: str, language: str) -> Dict[str, Any]:
    """
    Make a GET request to the API and return the JSON response.
    
    Args:
        url: The URL to request
        language: The language code for the request
    
    Returns:
        Dictionary containing the JSON response
    """
    headers = {"Accept-Language": language}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logger.error("Failed to fetch data: HTTP %s", response.status_code)
        return {"results": []}
    return response.json()


def get_paginated_data(base_url: str, language: str) -> List[Dict[str, Any]]:
    """
    Fetch all pages of data from a paginated API endpoint.
    
    Args:
        base_url: The base URL to request
        language: The language code for the request
    
    Returns:
        List of all results from all pages
    """
    results = []
    current_url = base_url
    while current_url:
        page = get_json_response(current_url, language)
        results.extend(page.get("results", []))
        current_url = page.get("next")  # will be None or empty when finished
    return results


def fetch_classes_data(quadrimester: str, language: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetch class data for a specific quadrimester.
    
    Args:
        quadrimester: The quadrimester code (e.g., "2023Q2")
        language: The language code for the request
    
    Returns:
        Dictionary containing the class data
    """
    url = f"{API_BASE_URL}/quadrimestres/{quadrimester}/classes.json?client_id={CLIENT_ID}&lang={language}"
    data = get_paginated_data(url, language)
    return {"results": data}


def fetch_subject_names(language: str) -> Dict[str, str]:
    """
    Fetch the names of all subjects.
    
    Args:
        language: The language code for the request
    
    Returns:
        Dictionary mapping subject codes to subject names
    """
    url = f"{API_BASE_URL}/assignatures.json?format=json&client_id={CLIENT_ID}&lang={language}"
    subjects = get_paginated_data(url, language)
    names = {item.get("id"): item.get("nom") for item in subjects if item.get("id") and item.get("nom")}
    return names


def generate_schedule_url(schedule_subjects: Dict[str, Dict[str, int]], quadrimester: str) -> str:
    """
    Generate a URL to view a schedule on the FIB website.
    
    Args:
        schedule_subjects: Dictionary mapping subject codes to group information
        quadrimester: The quadrimester code
    
    Returns:
        URL to view the schedule on the FIB website
    """
    base_url = "https://www.fib.upc.edu/en/studies/bachelors-degrees/bachelor-degree-informatics-engineering/timetables"
    params = f"?&class=true&lang=true&quad={quadrimester}"
    parts = []
    for subject, grp_info in schedule_subjects.items():
        parts.append(f"a={subject}_{grp_info['group']}")
        parts.append(f"a={subject}_{grp_info['subgroup']}")
    return base_url + params + "&" + "&".join(parts)
