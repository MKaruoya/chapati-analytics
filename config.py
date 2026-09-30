import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4"

# Data Configuration
DATA_FILE = "data/chapati_dataset.csv"
CACHE_DURATION = 3600

# Dataset Dimensions
STORES = 24
BRANCHES = 200
PRODUCTS = 4
DATE_RANGE = "March - September 2024"
MONTHS = ["03 March", "04 April", "05 May", "06 June", "07 July", "08 August", "09 September"]

# Visualization Colors
COLOR_PALETTE = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "danger": "#d62728",
    "warning": "#ff9896",
    "info": "#17becf"
}

# Thresholds
ANOMALY_THRESHOLD_ZSCORE = 2.5
ANOMALY_THRESHOLD_IQR = 1.5
LOW_SALES_THRESHOLD = 10
HIGH_RETURN_RATE = 0.15

# Page Configuration
PAGE_CONFIG = {
    "page_title": "Chapati Analytics",
    "page_icon": "🥙",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}
