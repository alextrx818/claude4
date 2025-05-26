#!/usr/bin/env python3
"""
ALL FETCHED JSON FIELDS ANALYZER
================================

This script analyzes the daily JSON data files to identify every unique field
being fetched from all API endpoints. It provides a comprehensive view of the
data structure without duplicates.
"""

import json
import os
import logging
from typing import Dict, Set, Any, List
from datetime import datetime
import config

# ─── LOGGER SETUP ──────────────────────────────────────────────────────────
logger = config.setup_logger('all_fetched_json_fields', 'all_fetched_json_fields.log')

def extract_fields_from_object(obj: Any, prefix: str = "", fields_set: Set[str] = None) -> Set[str]:
    """
    Recursively extract all field paths from a JSON object
    
    Args:
        obj: The JSON object to analyze
        prefix: Current field path prefix
        fields_set: Set to store unique field paths
    
    Returns:
        Set of unique field paths
    """
    if fields_set is None:
        fields_set = set()
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{prefix}.{key}" if prefix else key
            fields_set.add(current_path)
            extract_fields_from_object(value, current_path, fields_set)
    elif isinstance(obj, list) and obj:
        # Analyze first item in array to get structure
        if len(obj) > 0:
            array_prefix = f"{prefix}[0]" if prefix else "[0]"
            extract_fields_from_object(obj[0], array_prefix, fields_set)
    
    return fields_set

def find_latest_json_file() -> str:
    """
    Find the latest JSON data file
    
    Returns:
        Path to the latest JSON file
    """
    json_files = [f for f in os.listdir('.') if f.startswith('json_fetch_data_') and f.endswith('.json')]
    if not json_files:
        raise FileNotFoundError("No JSON data files found")
    
    return sorted(json_files)[-1]

def main():
    """
    Main function to analyze JSON fields
    """
    try:
        logger.info("🔍 STARTING JSON FIELDS ANALYSIS")
        logger.info("=" * 60)
        
        # Find the latest JSON file
        json_file = find_latest_json_file()
        logger.info(f"📁 Analyzing file: {json_file}")
        
        # Track fields by endpoint
        endpoint_fields = {}
        all_fields = set()
        entries_processed = 0
        
        # Read and parse the entire JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            logger.info("📖 Loading JSON data file...")
            
            try:
                # Try to load the entire file
                data = json.load(f)
                logger.info(f"✅ JSON file loaded successfully")
                
                # Check if it has the expected structure
                if 'entries' in data:
                    entries = data['entries']
                    logger.info(f"📊 Found {len(entries)} total entries")
                    
                    # Process each entry
                    for entry in entries:
                        if isinstance(entry, dict) and entry.get('type') == 'api_data':
                            endpoint = entry.get('endpoint', 'unknown')
                            entry_data = entry.get('data', {})
                            
                            if entry_data:
                                # Extract fields from this entry's data
                                entry_fields = extract_fields_from_object(entry_data)
                                
                                # Add to endpoint-specific fields
                                if endpoint not in endpoint_fields:
                                    endpoint_fields[endpoint] = set()
                                endpoint_fields[endpoint].update(entry_fields)
                                
                                # Add to all fields
                                all_fields.update(entry_fields)
                                
                                entries_processed += 1
                                
                                # Log progress every 50 entries
                                if entries_processed % 50 == 0:
                                    logger.info(f"📊 Processed {entries_processed} API entries...")
                    
                else:
                    logger.error("❌ JSON file doesn't have expected 'entries' structure")
                    return
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse JSON file: {str(e)}")
                return
            except Exception as e:
                logger.error(f"❌ Error reading file: {str(e)}")
                return
        
        logger.info(f"✅ Analysis complete! Processed {entries_processed} API entries")
        logger.info("=" * 60)
        
        # Log results by endpoint
        logger.info("📡 FIELDS BY ENDPOINT:")
        logger.info("=" * 60)
        
        for endpoint, fields in endpoint_fields.items():
            logger.info(f"")
            logger.info(f"🔹 {endpoint.upper()} ENDPOINT ({len(fields)} fields):")
            logger.info("-" * 40)
            
            for field in sorted(fields):
                logger.info(f"  • {field}")
        
        # Log summary
        logger.info("")
        logger.info("📊 SUMMARY:")
        logger.info("=" * 60)
        logger.info(f"Total endpoints analyzed: {len(endpoint_fields)}")
        logger.info(f"Total unique fields: {len(all_fields)}")
        logger.info(f"Entries processed: {entries_processed}")
        
        # Log all unique fields
        logger.info("")
        logger.info("🌟 ALL UNIQUE FIELDS (NO DUPLICATES):")
        logger.info("=" * 60)
        
        for field in sorted(all_fields):
            logger.info(f"  • {field}")
        
        logger.info("")
        logger.info("🎉 Field analysis completed successfully!")
        logger.info(f"📁 Results logged to: all_fetched_json_fields.log")
        
        # Also print summary to console
        print(f"\n✅ Analysis Complete!")
        print(f"📊 Found {len(all_fields)} unique fields across {len(endpoint_fields)} endpoints")
        print(f"📁 Detailed results logged to: all_fetched_json_fields.log")
        
        # Print a sample of fields to console
        if all_fields:
            print(f"\n📋 Sample of fields found:")
            sample_fields = sorted(list(all_fields))[:20]  # Show first 20 fields
            for field in sample_fields:
                print(f"  • {field}")
            if len(all_fields) > 20:
                print(f"  ... and {len(all_fields) - 20} more fields")
        
    except Exception as e:
        error_msg = f"❌ Error during analysis: {str(e)}"
        logger.error(error_msg)
        print(error_msg)
        raise

if __name__ == "__main__":
    main() 