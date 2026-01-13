#!/usr/bin/env python3
"""
Convert Operators Table to JSON
================================
Converts pipe-delimited table format in pay_Operators.txt to JSON format.
Reads table with headers and pipes (|) as delimiters.
"""

import json
from pathlib import Path
from datetime import datetime

def parse_table_to_json(input_file, output_txt, output_json):
    """Parse pipe-delimited table and convert to JSON"""
    
    print("=" * 80)
    print("CONVERTING OPERATORS TABLE TO JSON")
    print("=" * 80)
    print(f"\nInput:  {input_file}")
    print(f"Output: {output_txt}")
    print(f"        {output_json}")
    
    operators = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find header line (first line with column names)
    header_line = None
    data_start = 0
    
    for i, line in enumerate(lines):
        if line.strip() and not line.strip().startswith('-'):
            # This should be the header
            header_line = line
            data_start = i + 1
            break
    
    if not header_line:
        print("❌ ERROR: Could not find header line!")
        return
    
    # Parse headers
    headers = [h.strip() for h in header_line.split('|')]
    print(f"\n✓ Found {len(headers)} columns:")
    for h in headers:
        if h:
            print(f"  - {h}")
    
    # Skip separator line (dashes)
    while data_start < len(lines) and lines[data_start].strip().startswith('-'):
        data_start += 1
    
    # Parse data rows
    for line_num, line in enumerate(lines[data_start:], start=data_start + 1):
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Split by pipe
        values = [v.strip() for v in line.split('|')]
        
        # Create operator object
        operator = {}
        for i, header in enumerate(headers):
            if header and i < len(values):
                value = values[i]
                
                # Keep values exactly as they are - no conversions
                # Empty strings stay as empty strings
                # Numbers stay as strings unless explicitly numeric
                
                # Use original header names - no changes
                operator[header] = value
        
        if operator:
            operators.append(operator)
    
    print(f"\n✓ Parsed {len(operators)} operators")
    
    # Save as plain JSON array to .txt
    print(f"\n📝 Saving to {output_txt}...")
    with open(output_txt, 'w', encoding='utf-8') as f:
        json.dump(operators, f, indent=2, ensure_ascii=False)
    
    # Save to .json with same content
    print(f"📝 Saving to {output_json}...")
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(operators, f, indent=2, ensure_ascii=False)
    
    # Calculate file sizes
    txt_size = Path(output_txt).stat().st_size
    json_size = Path(output_json).stat().st_size
    
    print(f"\n✓ Conversion complete!")
    print(f"  - {output_txt}: {txt_size:,} bytes")
    print(f"  - {output_json}: {json_size:,} bytes")
    
    # Show sample
    if operators:
        print(f"\n📋 Sample operator:")
        sample = operators[0]
        for key, value in sample.items():
            print(f"  {key}: {value}")
    
    # Show statistics
    print(f"\n📊 Statistics:")
    statuses = {}
    for op in operators:
        status = op.get('statusName', 'Unknown')
        statuses[status] = statuses.get(status, 0) + 1
    
    print(f"  Total operators: {len(operators)}")
    print(f"  Unique statuses: {len(statuses)}")
    print(f"\n  Top 5 statuses:")
    for status, count in sorted(statuses.items(), key=lambda x: x[1], reverse=True)[:5]:
        pct = count / len(operators) * 100
        print(f"    - {status}: {count} ({pct:.1f}%)")
    
    print("\n" + "=" * 80)
    print("✅ CONVERSION COMPLETE")
    print("=" * 80)

def main():
    # File paths
    data_dir = Path(__file__).parent.parent / 'data'
    input_file = data_dir / 'pay_Operators.txt'
    output_txt = data_dir / 'pay_Operators.json.txt'  # Temp file
    output_json = data_dir / 'pay_Operators.json'
    
    # Backup original if JSON exists
    if output_json.exists():
        backup = data_dir / f'pay_Operators.json.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        print(f"⚠️  Backing up existing JSON to: {backup.name}")
        output_json.rename(backup)
    
    # Convert
    parse_table_to_json(input_file, output_txt, output_json)
    
    # Remove temp file (we only need .json)
    if output_txt.exists():
        output_txt.unlink()
        print(f"\n🗑️  Removed temporary file: {output_txt.name}")

if __name__ == '__main__':
    main()
