"""
Configuration management for AgriSense AI
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# ThingSpeak Configuration
THINGSPEAK_CHANNEL_ID = os.getenv("THINGSPEAK_CHANNEL_ID", "")
THINGSPEAK_READ_API_KEY = os.getenv("THINGSPEAK_READ_API_KEY", "")
THINGSPEAK_WRITE_API_KEY = os.getenv("THINGSPEAK_WRITE_API_KEY", "")

# Device Configuration
DEVICE_ID = os.getenv("DEVICE_ID", "ESP32_AGRISENSE_01")

# Application Settings
DATA_FRESHNESS_MINUTES = int(os.getenv("DATA_FRESHNESS_MINUTES", "30"))
CHART_REFRESH_INTERVAL_SECONDS = int(os.getenv("CHART_REFRESH_INTERVAL_SECONDS", "300"))
ENABLE_DEMO_MODE = os.getenv("ENABLE_DEMO_MODE", "true").lower() == "true"

# Sensor Validation Ranges
SENSOR_RANGES = {
    "soil_moisture": {"min": 0, "max": 100, "unit": "%"},
    "soil_ph": {"min": 0, "max": 14, "unit": "pH"},
    "temperature": {"min": -40, "max": 85, "unit": "°C"},
    "humidity": {"min": 0, "max": 100, "unit": "% RH"}
}

# Expected Operating Ranges (warnings, not hard limits)
EXPECTED_RANGES = {
    "soil_moisture": {"min": 10, "max": 90},
    "soil_ph": {"min": 4.0, "max": 9.0},
    "temperature": {"min": 0, "max": 50},
    "humidity": {"min": 20, "max": 95}
}

# Alert Thresholds (defaults)
ALERT_THRESHOLDS = {
    "soil_moisture": {
        "min": float(os.getenv("ALERT_SOIL_MOISTURE_MIN", "20")),
        "max": float(os.getenv("ALERT_SOIL_MOISTURE_MAX", "80"))
    },
    "soil_ph": {
        "min": float(os.getenv("ALERT_SOIL_PH_MIN", "5.5")),
        "max": float(os.getenv("ALERT_SOIL_PH_MAX", "8.0"))
    },
    "temperature": {
        "min": float(os.getenv("ALERT_TEMPERATURE_MIN", "10")),
        "max": float(os.getenv("ALERT_TEMPERATURE_MAX", "45"))
    },
    "humidity": {
        "min": float(os.getenv("ALERT_HUMIDITY_MIN", "30")),
        "max": float(os.getenv("ALERT_HUMIDITY_MAX", "90"))
    }
}

# Model Configuration
MODEL_PATH = MODELS_DIR / "crop_recommendation_model.joblib"
MODEL_METADATA_PATH = MODELS_DIR / "model_metadata.json"

# Dataset Configuration
DATASET_PATH = DATA_DIR / "crop_dataset.csv"

# ThingSpeak API Configuration
THINGSPEAK_BASE_URL = "https://api.thingspeak.com"
THINGSPEAK_TIMEOUT = 10  # seconds
THINGSPEAK_CACHE_DURATION = 60  # seconds

# Demo Mode Configuration
DEMO_MODE_ENABLED = ENABLE_DEMO_MODE or not THINGSPEAK_CHANNEL_ID
