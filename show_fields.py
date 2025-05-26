#!/usr/bin/env python3
"""
Simple Field Extractor - Shows JSON fields from API data
"""

import json
import os
from typing import Set

def extract_fields(obj, prefix="", fields=None):
    """Extract field names from JSON object"""
    if fields is None:
        fields = set()
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{prefix}.{key}" if prefix else key
            fields.add(current_path)
            extract_fields(value, current_path, fields)
    elif isinstance(obj, list) and obj:
        # Analyze first item in array
        extract_fields(obj[0], f"{prefix}[0]" if prefix else "[0]", fields)
    
    return fields

def main():
    # Find JSON file
    json_files = [f for f in os.listdir('.') if f.startswith('json_fetch_data_') and f.endswith('.json')]
    if not json_files:
        print("No JSON data files found")
        return
    
    json_file = sorted(json_files)[-1]  # Get latest
    print(f"Analyzing: {json_file}")
    
    try:
        with open(json_file, 'r') as f:
            # Read just the first part to avoid memory issues
            content = f.read(1000000)  # Read first 1MB
            if content.endswith(','):
                content = content[:-1] + ']}'
            elif not content.endswith('}'):
                content += ']}'
        
        # Try to parse partial JSON
        try:
            data = json.loads(content)
        except:
            # If that fails, try to find first complete entry
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '"type": "api_data"' in line:
                    # Found an API entry, try to extract it
                    entry_start = i
                    brace_count = 0
                    entry_lines = []
                    for j in range(entry_start, min(entry_start + 100, len(lines))):
                        entry_lines.append(lines[j])
                        brace_count += lines[j].count('{') - lines[j].count('}')
                        if brace_count == 0 and j > entry_start:
                            break
                    
                    entry_text = '\n'.join(entry_lines)
                    if entry_text.endswith(','):
                        entry_text = entry_text[:-1]
                    
                    try:
                        entry = json.loads(entry_text)
                        if 'data' in entry:
                            print(f"\nFields found in {entry.get('endpoint', 'unknown')} endpoint:")
                            fields = extract_fields(entry['data'])
                            for field in sorted(fields):
                                print(f"  • {field}")
                            return
                    except:
                        continue
            
            print("Could not parse JSON data")
            return
        
        # If we successfully parsed the data
        if 'entries' in data:
            endpoints = {}
            for entry in data['entries'][:10]:  # Look at first 10 entries
                if entry.get('type') == 'api_data':
                    endpoint = entry.get('endpoint', 'unknown')
                    if endpoint not in endpoints:
                        endpoints[endpoint] = extract_fields(entry.get('data', {}))
            
            print(f"\n=== FIELDS FOUND IN API ENDPOINTS ===")
            for endpoint, fields in endpoints.items():
                print(f"\n📡 {endpoint.upper()} ({len(fields)} fields):")
                for field in sorted(fields):
                    print(f"  • {field}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 