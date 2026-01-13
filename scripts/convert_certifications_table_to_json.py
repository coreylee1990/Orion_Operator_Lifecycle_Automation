#!/usr/bin/env python3
"""
Convert Certifications Table to JSON
=====================================
Converts pipe-delimited table format in pay_Certifications.txt to JSON format.
Reads table with headers and pipes (|) as delimiters.
"""

import json
from pathlib import Path
from datetime import datetime

def parse_table_to_json(input_file, output_txt, output_json):
    """Parse pipe-delimited table and convert to JSON"""
    
    print("=" * 80)
    print("CONVERTING CERTIFICATIONS TABLE TO JSON")
    print("=" * 80)
    print(f"\nInput:  {input_file}")
    print(f"Output: {output_txt}")
    print(f"        {output_json}")
    
    certifications = []
    
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
        
        # Create certification object
        cert = {}
        for i, header in enumerate(headers):
            if header and i < len(values):
                value = values[i]
                
                # Keep values exactly as they are - no conversions
                # Empty strings stay as empty strings
                # Numbers stay as strings unless explicitly numeric
                
                # Use original header names - no changes
                cert[header] = value
        
        if cert:
            certifications.append(cert)
    
    print(f"\n✓ Parsed {len(certifications)} certifications\n")
    
    # Save to files
    print(f"📝 Saving to {output_txt}...")
    with open(output_txt, 'w', encoding='utf-8') as f:
        json.dump(certifications, f, indent=2, ensure_ascii=False)
    
    print(f"📝 Saving to {output_json}...")
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(certifications, f, indent=2, ensure_ascii=False)
    
    # Get file sizes
    size_txt = output_txt.stat().st_size
    size_json = output_json.stat().st_size
    
    print(f"\n✓ Conversion complete!")
    print(f"  - {output_txt}: {size_txt:,} bytes")
    print(f"  - {output_json}: {size_json:,} bytes")
    
    # Show sample certification
    if certifications:
        print("\n📋 Sample certification:")
        sample = certifications[0]
        for key in ['ID', 'FirstName', 'LastName', 'Cert', 'Date', 'CertificationID', 
                    'isApproved', 'ApprovedDate', 'StatusName', 'OrderID']:
            if key in sample:
                print(f"  {key}: {sample[key]}")
    
    # Statistics
    print("\n📊 Statistics:")
    print(f"  Total certifications: {len(certifications)}")
    
    # Count unique operators
    unique_operators = set()
    for cert in certifications:
        if cert.get('ID'):
            unique_operators.add(cert['ID'])
    print(f"  Unique operators: {len(unique_operators)}")
    
    # Count by status
    status_counts = {}
    for cert in certifications:
        status = cert.get('StatusName', 'Unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"\n  Top 5 statuses by certification count:")
    for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        pct = (count / len(certifications)) * 100
        print(f"    - {status}: {count} ({pct:.1f}%)")
    
    # Count by cert type
    cert_type_counts = {}
    for cert in certifications:
        cert_name = cert.get('Cert', 'Unknown')
        cert_type_counts[cert_name] = cert_type_counts.get(cert_name, 0) + 1
    
    print(f"\n  Top 10 certification types:")
    for cert_name, count in sorted(cert_type_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        pct = (count / len(certifications)) * 100
        print(f"    - {cert_name}: {count} ({pct:.1f}%)")

def main():
    # Paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_dir = project_root / 'data'
    
    input_file = data_dir / 'pay_Certifications.txt'
    output_txt = data_dir / 'pay_Certifications.json.txt'
    output_json = data_dir / 'pay_Certifications.json'
    
    # Check if input exists
    if not input_file.exists():
        print(f"❌ ERROR: Input file not found: {input_file}")
        return 1
    
    # Backup existing JSON if it exists
    if output_json.exists():
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = data_dir / f'pay_Certifications.json.backup.{timestamp}'
        output_json.rename(backup_file)
        print(f"⚠️  Backing up existing JSON to: {backup_file.name}")
    
    # Convert
    parse_table_to_json(input_file, output_txt, output_json)
    
    # Remove temp .txt file
    if output_txt.exists():
        output_txt.unlink()
        print(f"\n🗑️  Removed temporary file: {output_txt.name}")
    
    print("\n" + "=" * 80)
    print("✅ CONVERSION COMPLETE")
    print("=" * 80)
    
    return 0

if __name__ == '__main__':
    exit(main())
