"""
Constants used throughout the FIB Manager application.
"""

# API constants
API_BASE_URL = "https://api.fib.upc.edu/v2"
CLIENT_ID = "77qvbbQqni4TcEUsWvUCKOG1XU7Hr0EfIs4pacRz"
LANGUAGE_MAPPING = {"en": "en", "es": "es", "ca": "ca", "": "en"}
DEFAULT_LANGUAGE = "ca"

# UI constants
FILLED_BAR_COLOR = "#AA0000 bold"  # dark red bar
EMPTY_BAR_COLOR = "#666666 bold"   # secondary color
TEXT_COLOR = "#666666 bold"        # primary color
NUMBER_COLOR = "#FF5555 bold"      # light red for numbers

# Language mapping
LANGUAGE_MAP = {
    "catala": "ca", "català": "ca", "catalan": "ca", "ca": "ca",
    "castella": "es", "castellà": "es", "castellano": "es",
    "espanol": "es", "español": "es", "spanish": "es", "es": "es",
    "english": "en", "anglés": "en", "angles": "en",
    "inglés": "en", "ingles": "en", "en": "en",
}

LANG_FLAGS = {"en": "ENG", "es": "ESP", "ca": "CAT"}

# UI Theme colors
SUBJECT_COLORS = [
    "#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", 
    "#BAE1FF", "#FFECB3", "#D7BDE2", "#AED6F1",
]

# Day names for display
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
