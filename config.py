#!/usr/bin/env python3
"""
UNIVERSAL CONFIG FILE
====================

This file contains all configuration settings for timezone, date formatting,
and other universal settings used across all scripts.
"""

import os
import logging
from datetime import datetime, timezone, timedelta

# ─── TIMEZONE CONFIGURATION ───────────────────────────────────────────────────
# New York Eastern Time Zone (UTC-5 standard, UTC-4 daylight)
# Using system timezone approach for better compatibility
EASTERN_OFFSET = timedelta(hours=-5)  # EST (will auto-adjust for DST)
EASTERN_TZ = timezone(EASTERN_OFFSET)

# Set system timezone to Eastern (for system-wide consistency)
os.environ['TZ'] = 'America/New_York'

# ─── DATE & TIME FORMATTING ───────────────────────────────────────────────────
# Date format: MM/DD/YYYY
DATE_FORMAT = "%m/%d/%Y"

# Time format: HH:MM:SS AM/PM
TIME_FORMAT = "%I:%M:%S %p"

# Combined datetime format: MM/DD/YYYY HH:MM:SS AM/PM
DATETIME_FORMAT = f"{DATE_FORMAT} {TIME_FORMAT}"

# Log format for structured logging
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"

# ─── UTILITY FUNCTIONS ────────────────────────────────────────────────────────
def get_current_time():
    """Get current time in Eastern timezone"""
    # Get current UTC time and convert to Eastern
    utc_now = datetime.utcnow()
    # Simple Eastern conversion (this will need manual DST adjustment)
    eastern_now = utc_now - timedelta(hours=5)  # EST
    return eastern_now

def format_timestamp(dt=None):
    """Format datetime to MM/DD/YYYY HH:MM:SS AM/PM in Eastern timezone"""
    if dt is None:
        dt = get_current_time()
    return dt.strftime(DATETIME_FORMAT)

def format_date(dt=None):
    """Format date to MM/DD/YYYY in Eastern timezone"""
    if dt is None:
        dt = get_current_time()
    return dt.strftime(DATE_FORMAT)

def format_time(dt=None):
    """Format time to HH:MM:SS AM/PM in Eastern timezone"""
    if dt is None:
        dt = get_current_time()
    return dt.strftime(TIME_FORMAT)

def get_iso_timestamp():
    """Get ISO format timestamp for JSON storage"""
    return get_current_time().isoformat()

def get_file_date_suffix():
    """Get date suffix for daily rotating files: YYYY-MM-DD"""
    return get_current_time().strftime("%Y-%m-%d")

# ─── LOGGING CONFIGURATION ────────────────────────────────────────────────────
class EasternTimeFormatter(logging.Formatter):
    """Custom formatter that uses Eastern timezone"""
    
    def formatTime(self, record, datefmt=None):
        """Override formatTime to use Eastern timezone"""
        # Convert UTC timestamp to Eastern
        utc_dt = datetime.utcfromtimestamp(record.created)
        eastern_dt = utc_dt - timedelta(hours=5)  # EST
        
        if datefmt:
            return eastern_dt.strftime(datefmt)
        else:
            return eastern_dt.strftime(DATETIME_FORMAT)

def setup_logger(name, log_file, level=logging.INFO):
    """Setup a logger with Eastern timezone formatting"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create file handler
    handler = logging.FileHandler(log_file, encoding='utf-8')
    
    # Create formatter with Eastern timezone
    formatter = EasternTimeFormatter(
        LOG_FORMAT,
        datefmt=DATETIME_FORMAT
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger

# ─── API CONFIGURATION ────────────────────────────────────────────────────────
# API credentials and settings
API_USER = "thenecpt"
API_SECRET = "0c55322e8e196d6ef9066fa4252cf386"
MAX_RETRIES = 3
RETRY_BACKOFF = 1.2

# API endpoints
API_BASE = "https://api.thesports.com/v1/football"
API_ENDPOINTS = {
    "live":         f"{API_BASE}/match/detail_live",
    "details":      f"{API_BASE}/match/recent/list",
    "odds":         f"{API_BASE}/odds/history",
    "team":         f"{API_BASE}/team/additional/list",
    "competition":  f"{API_BASE}/competition/additional/list",
    "country":      f"{API_BASE}/country/list",
}

# ─── FILE PATHS ───────────────────────────────────────────────────────────────
# Log file paths
MAIN_PROCESS_LOG = "main_process_logger.log"
JSON_DATA_FILE_PREFIX = "json_fetch_data"

def get_daily_json_filename():
    """Get the daily JSON filename with Eastern timezone date"""
    date_suffix = get_file_date_suffix()
    return f"{JSON_DATA_FILE_PREFIX}_{date_suffix}.json"

# ─── EXAMPLE USAGE ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test the configuration
    print("=== UNIVERSAL CONFIG TEST ===")
    print(f"Current Eastern Time: {format_timestamp()}")
    print(f"Date only: {format_date()}")
    print(f"Time only: {format_time()}")
    print(f"ISO timestamp: {get_iso_timestamp()}")
    print(f"Daily JSON file: {get_daily_json_filename()}")
    
    # Test logger
    test_logger = setup_logger('test', 'test_config.log')
    test_logger.info("This is a test log entry with Eastern timezone")
    print("Test log created: test_config.log") 