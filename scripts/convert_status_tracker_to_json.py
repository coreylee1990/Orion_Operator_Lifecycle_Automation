#!/usr/bin/env python3
"""
Convert pay_StatusTracker.txt to JSON format.
"""

import json
from pathlib import Path

def convert_status_tracker_to_json():
    """Convert StatusTracker data to JSON format."""
    
    input_file = Path(__file__).parent.parent / 'data' / 'pay_StatusTracker.txt'
    output_file = Path(__file__).parent.parent / 'data' / 'pay_StatusTracker.json'
    
    print(f"Reading from: {input_file}")
    
    # Read the file
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if not lines:
        print("Error: File is empty")
        return
    
    # Parse pipe-delimited data
    # First line is header
    header_line = lines[0].strip()
    headers = [h.strip() for h in header_line.split('|')]
    
    print(f"✓ Found columns: {headers}")
    
    # Skip separator line (line with dashes)
    data_lines = [line for line in lines[2:] if line.strip() and not line.strip().startswith('-')]
    
    records = []
    for line in data_lines:
        values = [v.strip() for v in line.split('|')]
        
        # Create record dict
        if len(values) == len(headers):
            record = {}
            for i, header in enumerate(headers):
                # Convert empty strings to None/null
                value = values[i] if values[i] else None
                record[header] = value
            records.append(record)
    
    print(f"✓ Parsed {len(records)} status tracker records")
    
    # Wrap in standard format
    output_data = {
        'statusTracker': records
    }
    
    # Save as formatted JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved to: {output_file}")
    print(f"✓ Total records: {len(records)}")
    
    # Show sample record
    if records:
        print("\nSample record:")
        print(json.dumps(records[0], indent=2))

if __name__ == '__main__':
    convert_status_tracker_to_json()
