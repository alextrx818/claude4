#!/usr/bin/env python3
"""
JSON FETCH (STEP 1) - Centralized JSON Logging Version
======================================================

This script fetches data from all thesports.com API endpoints
and logs everything to a centralized daily JSON file that rotates at midnight.
"""

import os
import requests
import time
import hashlib
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import shutil
import config  # Import universal config

# ─── credentials & retry settings ───────────────────────────────────────────────
USER = os.getenv("API_USER", "thenecpt")
SECRET = os.getenv("API_SECRET", "0c55322e8e196d6ef9066fa4252cf386")
MAX_RETRIES = 3
RETRY_BACKOFF = 1.2

# ─── API ENDPOINTS ─────────────────────────────────────────────────────────────
_BASE = "https://api.thesports.com/v1/football"
_URLS = {
    "live":         f"{_BASE}/match/detail_live",
    "details":      f"{_BASE}/match/recent/list",
    "odds":         f"{_BASE}/odds/history",
    "team":         f"{_BASE}/team/additional/list",
    "competition":  f"{_BASE}/competition/additional/list",
    "country":      f"{_BASE}/country/list",
}

# ─── MAIN PROCESS LOGGER SETUP ────────────────────────────────────────────────
# Use universal config for logger setup
main_logger = config.setup_logger('main_process', config.MAIN_PROCESS_LOG)

# ─── JSON FILE MANAGEMENT ─────────────────────────────────────────────────────
def get_json_filename():
    """Get the current JSON filename based on today's date in Eastern timezone"""
    return config.get_daily_json_filename()

def rotate_json_file_if_needed():
    """Rotate JSON file if it's a new day"""
    current_file = get_json_filename()
    
    # Check if we need to rotate (if current file doesn't exist for today)
    if not os.path.exists(current_file):
        # Archive any existing files from previous days
        for file in os.listdir('.'):
            if file.startswith('json_fetch_data_') and file.endswith('.json') and file != current_file:
                # Move to archive (keep last 30 days)
                archive_name = f"archive_{file}"
                if os.path.exists(archive_name):
                    os.remove(archive_name)
                shutil.move(file, archive_name)
        
        # Create new file with initial structure
        initial_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "created_at": datetime.now().isoformat(),
            "entries": []
        }
        with open(current_file, 'w') as f:
            json.dump(initial_data, f, indent=2)
    
    return current_file

def append_to_json_file(entry: Dict[str, Any]):
    """Append an entry to the current JSON file"""
    filename = rotate_json_file_if_needed()
    
    # Read existing data
    with open(filename, 'r') as f:
        data = json.load(f)
    
    # Append new entry
    data["entries"].append(entry)
    data["last_updated"] = datetime.now().isoformat()
    
    # Write back to file
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

class APIError(Exception):
    """Custom exception for API related errors"""
    pass

def generate_signature(params: Dict[str, Any]) -> str:
    """Generate API signature using MD5 hash"""
    sorted_params = dict(sorted(params.items()))
    string_to_sign = '&'.join([f"{k}={v}" for k, v in sorted_params.items()])
    signature = hashlib.md5(string_to_sign.encode()).hexdigest()
    return signature

def make_api_request(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Make authenticated API request to specified endpoint"""
    if endpoint not in _URLS:
        raise APIError(f"Invalid endpoint: {endpoint}")
    
    url = _URLS[endpoint]
    
    # Base request parameters
    request_params = {
        "user": USER,
        "secret": SECRET,
        "timestamp": str(int(time.time()))
    }
    
    # Add additional parameters if provided
    if params:
        request_params.update(params)
    
    # Add signature
    request_params["sign"] = generate_signature(request_params)
    
    try:
        # Make the API request
        response = requests.get(url, params=request_params)
        response.raise_for_status()
        data = response.json()
        
        # Check API response status
        if "code" not in data:
            raise APIError("Invalid API response format - missing status code")
            
        status_code = data.get("code")
        
        if status_code == 404:
            raise APIError("Resource does not exist")
        elif status_code == 9999:
            raise APIError("Unknown API error")
        elif status_code != 0:  # 0 is success
            raise APIError(f"API Error: {data.get('message', 'Unknown error')}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        raise APIError(f"Request failed: {str(e)}")

def log_api_data(endpoint: str, data: Dict[str, Any], records_count: int):
    """Log API data to centralized JSON file"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": "api_data",
        "endpoint": endpoint,
        "url": _URLS[endpoint],
        "records_count": records_count,
        "status": "success",
        "data": data
    }
    
    append_to_json_file(log_entry)

def log_api_error(endpoint: str, error: str):
    """Log API error to centralized JSON file"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": "api_error",
        "endpoint": endpoint,
        "url": _URLS[endpoint],
        "status": "error",
        "error": error
    }
    
    append_to_json_file(log_entry)

def fetch_all_endpoints():
    """Fetch data from all configured API endpoints"""
    print("🚀 Starting data collection from all API endpoints")
    main_logger.info("🚀 Starting data collection from all API endpoints")
    
    results = {}
    
    for endpoint_name in _URLS.keys():
        try:
            print(f"📡 Fetching {endpoint_name} endpoint...")
            main_logger.info(f"📡 Fetching {endpoint_name} endpoint...")
            
            # Make API request
            data = make_api_request(endpoint_name)
            
            # Count records
            records_count = len(data.get("results", [])) if "results" in data else 0
            
            # Log the data to centralized JSON file
            log_api_data(endpoint_name, data, records_count)
            
            results[endpoint_name] = {
                "status": "success",
                "records": records_count
            }
            
            print(f"✅ {endpoint_name}: {records_count} records")
            main_logger.info(f"✅ {endpoint_name}: {records_count} records")
            
            # Add delay between requests to be respectful
            time.sleep(1)
            
        except APIError as e:
            error_msg = str(e)
            log_api_error(endpoint_name, error_msg)
            results[endpoint_name] = {
                "status": "failed",
                "error": error_msg,
                "records": 0
            }
            print(f"❌ {endpoint_name}: {error_msg}")
            main_logger.error(f"❌ {endpoint_name}: {error_msg}")
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            log_api_error(endpoint_name, error_msg)
            results[endpoint_name] = {
                "status": "error",
                "error": error_msg,
                "records": 0
            }
            print(f"❌ {endpoint_name}: {error_msg}")
            main_logger.error(f"❌ {endpoint_name}: {error_msg}")
    
    return results

def print_summary(results: Dict[str, Dict[str, Any]]):
    """Print summary of fetch results"""
    print("=" * 60)
    print("📊 FETCH SUMMARY")
    print("=" * 60)
    main_logger.info("=" * 60)
    main_logger.info("📊 FETCH SUMMARY")
    main_logger.info("=" * 60)
    
    total_endpoints = len(results)
    successful = sum(1 for r in results.values() if r["status"] == "success")
    total_records = sum(r["records"] for r in results.values())
    
    print(f"Total endpoints: {total_endpoints}")
    print(f"Successful: {successful}")
    print(f"Failed: {total_endpoints - successful}")
    print(f"Total records fetched: {total_records}")
    
    main_logger.info(f"Total endpoints: {total_endpoints}")
    main_logger.info(f"Successful: {successful}")
    main_logger.info(f"Failed: {total_endpoints - successful}")
    main_logger.info(f"Total records fetched: {total_records}")
    
    print("\nDetailed results:")
    main_logger.info("Detailed results:")
    for endpoint, result in results.items():
        status_icon = "✅" if result["status"] == "success" else "❌"
        detail_line = f"{status_icon} {endpoint:12} | {result['status']:12} | {result['records']:6} records"
        print(detail_line)
        main_logger.info(detail_line)
        if result.get('error'):
            error_line = f"    Error: {result['error']}"
            print(error_line)
            main_logger.error(error_line)
    
    # Log summary to JSON file
    summary_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": "summary",
        "total_endpoints": total_endpoints,
        "successful": successful,
        "failed": total_endpoints - successful,
        "total_records": total_records,
        "results": results
    }
    append_to_json_file(summary_entry)

def main():
    """Main function to fetch all API data"""
    json_file = get_json_filename()
    print("JSON FETCH (STEP 1) - Starting data collection")
    print(f"User: {USER}")
    print(f"Endpoints to fetch: {len(_URLS)}")
    print(f"JSON file: {json_file} (rotates daily at midnight)")
    
    main_logger.info("JSON FETCH (STEP 1) - Starting data collection")
    main_logger.info(f"User: {USER}")
    main_logger.info(f"Endpoints to fetch: {len(_URLS)}")
    main_logger.info(f"JSON file: {json_file} (rotates daily at midnight)")
    
    try:
        # Fetch data from all endpoints
        results = fetch_all_endpoints()
        
        # Print summary
        print_summary(results)
        
        print("🎉 Data collection completed!")
        print(f"📁 All data logged to: {json_file}")
        
        main_logger.info("🎉 Data collection completed!")
        main_logger.info(f"📁 All data logged to: {json_file}")
        
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        main_logger.error(f"❌ Fatal error: {str(e)}")

if __name__ == "__main__":
    main() 