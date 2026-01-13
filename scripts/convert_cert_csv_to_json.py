#!/usr/bin/env python3
"""
Convert certification CSV export to JSON format.
Reads CSV from externalSources and outputs to data/pay_Certifications.txt and .json
"""

import csv
import json
import sys
from pathlib import Path

def convert_csv_to_json(csv_file: Path, output_txt: Path, output_json: Path):
    """Convert CSV to JSON format and write to both .txt and .json files."""
    
    certifications = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                certifications.append(row)
        
        # Create output structure
        output_data = {
            "certifications": certifications,
            "totalCount": len(certifications),
            "metadata": {
                "source": csv_file.name,
                "description": "Certification records with all fields from database export"
            }
        }
        
        # Write both files with identical content
        for output_file in [output_txt, output_json]:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2)
        
        return True
    
    except Exception as e:
        print(f"Error processing file: {e}", file=sys.stderr)
        return False

def main():
    # Setup paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    csv_file = project_root / 'externalSources' / '_SELECT_o_ID_AS_OperatorID_o_FirstName_o_LastName_o_DivisionID_o_202601101816.csv'
    output_txt = project_root / 'data' / 'pay_Certifications.txt'
    output_json = project_root / 'data' / 'pay_Certifications.json'
    
    print("=" * 80)
    print("Certification CSV to JSON Converter")
    print("=" * 80)
    print(f"Reading CSV from:  {csv_file}")
    print(f"Writing TXT to:    {output_txt}")
    print(f"Writing JSON to:   {output_json}")
    print()
    
    if not csv_file.exists():
        print(f"⚠️  CSV file not found: {csv_file}", file=sys.stderr)
        sys.exit(1)
    
    # Convert
    success = convert_csv_to_json(csv_file, output_txt, output_json)
    
    print()
    print("=" * 80)
    if success:
        print("✅ Conversion complete! Created both .txt and .json files")
    else:
        print("❌ Conversion failed", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
