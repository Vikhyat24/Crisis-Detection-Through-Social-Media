"""
Configuration file for Crisis Detection GUI Application
Modify these settings to customize the application behavior
"""

# ============================================================
# DEFAULT GEOLOCATION PARAMETERS
# ============================================================

DEFAULT_LATITUDE = 24.7941004
DEFAULT_LONGITUDE = 93.1170986
DEFAULT_RADIUS = "1000km"
DEFAULT_PLACE_NAME = "Tamil Nadu"
DEFAULT_MIN_TWEETS = 50

# ============================================================
# CRISIS DETECTION PARAMETERS
# ============================================================

# Default confidence threshold for crisis classification (0.0 - 1.0)
DEFAULT_CONFIDENCE_THRESHOLD = 0.5

# Confidence levels for urgency classification
URGENCY_CRITICAL = 0.8      # >= 80% confidence
URGENCY_HIGH = 0.6          # >= 60% confidence
URGENCY_MEDIUM = 0.4        # >= 40% confidence
URGENCY_LOW = 0.0           # < 40% confidence

# ============================================================
# CRISIS KEYWORDS
# ============================================================

CRISIS_KEYWORDS = [
    'emergency', 'disaster', 'flood', 'earthquake', 'fire', 'accident',
    'crisis', 'danger', 'urgent', 'help needed', 'evacuation', 'injury',
    'severe', 'affected', 'rescue', 'alert', 'storm', 'cyclone', 'danger',
    'injured', 'death', 'hospital', 'police', 'ambulance', 'urgent',
    'critical', 'emergency', 'serious', 'severe', 'devastating',
    'collapse', 'trapped', 'stranded', 'missing', 'lost'
]

# ============================================================
# MAP SETTINGS
# ============================================================

# Map tiles options: 'OpenStreetMap', 'CartoDB positron', 'CartoDB voyager', 'Stamen Terrain'
DEFAULT_MAP_TILE = 'OpenStreetMap'
DEFAULT_ZOOM_LEVEL = 6

# Marker colors for different confidence levels
MARKER_COLOR_HIGH = 'red'       # Confidence >= 80%
MARKER_COLOR_MEDIUM = 'orange'  # Confidence 60-80%
MARKER_COLOR_LOW = 'yellow'     # Confidence 30-60%

# Heatmap settings
HEATMAP_RADIUS = 25
HEATMAP_BLUR = 20
HEATMAP_MIN_OPACITY = 0.3

# ============================================================
# FILE PATHS
# ============================================================

# Output directory for maps and exports
import os as _os
OUTPUT_DIR = _os.path.dirname(_os.path.abspath(__file__))

# Model file paths
MODEL_FILE = "final_mlp_model.joblib"
VECTORIZER_FILE = "tfidf_vectorizer.joblib"

# Sample data files
SAMPLE_DATA_FILE = "cleaned_tweets_data_with_punctuation.csv"
LATEST_DATA_FILE = "latest_tweets_data.csv"

# ============================================================
# EXPORT SETTINGS
# ============================================================

# Export filename formats
EXPORT_TWEETS_FORMAT = "tweets_export_{timestamp}.csv"
EXPORT_CRISIS_TWEETS_FORMAT = "crisis_tweets_{timestamp}.csv"

# Map output filenames
MAP_OUTPUT_FILE = "crisis_map.html"
HEATMAP_OUTPUT_FILE = "crisis_heatmap.html"
COMBINED_MAP_FILE = "combined_map.html"
STATISTICS_MAP_FILE = "statistics_map.html"

# ============================================================
# TEXT PROCESSING SETTINGS
# ============================================================

# Stop words - can be extended
ADDITIONAL_STOP_WORDS = []

# TF-IDF vectorizer settings
TFIDF_MAX_FEATURES = 5000
TFIDF_NGRAM_RANGE = (1, 2)

# ============================================================
# ML MODEL SETTINGS
# ============================================================

# MLP Classifier parameters
MLP_HIDDEN_LAYERS = (256, 128)
MLP_MAX_ITERATIONS = 500
MLP_ACTIVATION = 'relu'
MLP_SOLVER = 'adam'

# ============================================================
# LOGGING SETTINGS
# ============================================================

# Enable detailed logging
ENABLE_LOGGING = True
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# ============================================================
# APPLICATION UI SETTINGS
# ============================================================

# Window size
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# Font settings
TITLE_FONT = ("Helvetica", 16, "bold")
LABEL_FONT = ("Helvetica", 12, "bold")
TEXT_FONT = ("Helvetica", 10)
MONO_FONT = ("Courier", 9)

# Colors
BG_COLOR = "#f0f0f0"
HIGHLIGHT_COLOR = "#d32f2f"
SUCCESS_COLOR = "#2e7d32"
WARNING_COLOR = "#f57c00"
ERROR_COLOR = "#c62828"

# ============================================================
# RATE LIMITING (for future API integration)
# ============================================================

# Tweet collection rate limit (tweets per second)
RATE_LIMIT = 1.0

# API timeout in seconds
API_TIMEOUT = 30

# ============================================================
# DATA VALIDATION
# ============================================================

# Minimum tweet length (characters)
MIN_TWEET_LENGTH = 10

# Maximum tweet length
MAX_TWEET_LENGTH = 280

# Latitude range
LAT_MIN = -90
LAT_MAX = 90

# Longitude range
LON_MIN = -180
LON_MAX = 180

# ============================================================
# COLLECTION SETTINGS
# ============================================================

# Enable threading for collection
ENABLE_THREADING = True

# Collection timeout (seconds)
COLLECTION_TIMEOUT = 3600

# Data source options: 'sample', 'csv', 'api', 'selenium'
AVAILABLE_SOURCES = ['csv', 'sample']
DEFAULT_SOURCE = 'csv'

# ============================================================
# FEATURE FLAGS
# ============================================================

# Enable real-time collection
ENABLE_REALTIME_COLLECTION = True

# Enable ML model loading
ENABLE_ML_MODEL = True

# Enable heuristic fallback detection
ENABLE_HEURISTIC_DETECTION = True

# Enable map generation
ENABLE_MAP_GENERATION = True

# Enable data export
ENABLE_DATA_EXPORT = True

# ============================================================
# PERFORMANCE SETTINGS
# ============================================================

# Batch processing size
BATCH_SIZE = 100

# Maximum tweets to process at once
MAX_BATCH_TWEETS = 10000

# Cache results
ENABLE_CACHING = True

# ============================================================
# EMERGENCY CONTACT (for future integration)
# ============================================================

# Emergency services contact information
EMERGENCY_SERVICES = {
    'police': '100',
    'ambulance': '102',
    'fire': '101',
    'disaster_management': '1070'
}
