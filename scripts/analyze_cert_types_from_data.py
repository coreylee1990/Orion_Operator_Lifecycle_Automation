#!/usr/bin/env python3
"""
Analyze certification types from local data files
Since pay_CertTypes.txt is corrupted, we'll look at:
1. The Operators data to see what certification fields exist
2. Any certification-related columns in the data
"""

import json
import os
from collections import Counter, defaultdict

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def load_json_file(filename):
    """Load a JSON data file"""
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

def analyze_operators():
    """Analyze operators data for certification-related fields"""
    print("=" * 80)
    print("ANALYZING OPERATORS DATA FOR CERTIFICATION FIELDS")
    print("=" * 80)
    
    operators = load_json_file('pay_Operators.txt')
    if not operators:
        return
    
    print(f"\nTotal operators: {len(operators)}")
    
    # Get all field names
    if operators:
        all_fields = set()
        for op in operators:
            all_fields.update(op.keys())
        
        # Find certification-related fields
        cert_fields = [f for f in sorted(all_fields) if any(keyword in f.lower() 
                      for keyword in ['cert', 'license', 'document', 'background', 
                                     'check', 'verification', 'ssn', 'w9', 'id'])]
        
        print("\n" + "=" * 80)
        print("CERTIFICATION-RELATED FIELDS IN OPERATORS:")
        print("=" * 80)
        for field in cert_fields:
            print(f"  - {field}")
        
        # Sample values for cert fields
        if cert_fields:
            print("\n" + "=" * 80)
            print("SAMPLE VALUES (first 5 operators):")
            print("=" * 80)
            for i, op in enumerate(operators[:5]):
                print(f"\n--- Operator {i+1}: {op.get('FirstName', '')} {op.get('LastName', '')} ---")
                print(f"    Division: {op.get('DivisionID', 'N/A')}")
                print(f"    Status: {op.get('CurrentStatus', 'N/A')}")
                for field in cert_fields:
                    value = op.get(field)
                    if value is not None and value != '':
                        print(f"    {field}: {value}")
        
        # Look for boolean certification flags
        print("\n" + "=" * 80)
        print("ANALYZING CERTIFICATION FLAGS (Boolean fields):")
        print("=" * 80)
        
        boolean_cert_fields = [f for f in cert_fields if any(
            op.get(f) in [True, False, 'true', 'false', 1, 0] for op in operators[:20]
        )]
        
        if boolean_cert_fields:
            for field in boolean_cert_fields:
                true_count = sum(1 for op in operators if op.get(field) in [True, 'true', 1])
                false_count = sum(1 for op in operators if op.get(field) in [False, 'false', 0])
                print(f"\n  {field}:")
                print(f"    True/Yes: {true_count}")
                print(f"    False/No: {false_count}")

def analyze_status_types():
    """Analyze status types for certification requirements"""
    print("\n" + "=" * 80)
    print("ANALYZING STATUS TYPES FOR CERTIFICATION REQUIREMENTS")
    print("=" * 80)
    
    statuses = load_json_file('pay_StatusTypes.txt')
    if not statuses:
        return
    
    # Group by division and check CertFlag
    divisions = defaultdict(list)
    
    for status in statuses:
        if status.get('CertFlag') == True or status.get('CertFlag') == 1:
            div = status.get('DivisionID', 'Unknown')
            divisions[div].append({
                'OrderID': status.get('OrderID'),
                'Status': status.get('Status'),
                'CertFlag': status.get('CertFlag')
            })
    
    print(f"\nStatuses requiring certifications (CertFlag=True):")
    print("\nTarget divisions:")
    target_divs = ['2 - IL', '3 - TX', '5 - CA', '6 - FL', '7 - MI', '8 - OH', '10 - OR', '11 - GA', '12 - PA']
    excluded_divs = ['PA - BROOKES', '2 - LAHORE']  # Divisions to exclude from analysis
    
    for div_prefix in target_divs:
        div_statuses = []
        for div, statuses_list in divisions.items():
            if div.startswith(div_prefix):
                div_statuses.extend(statuses_list)
        
        if div_statuses:
            print(f"\n{div_prefix}:")
            for st in sorted(div_statuses, key=lambda x: int(x['OrderID'])):
                print(f"  Step {st['OrderID']}: {st['Status']}")

def look_for_cert_type_patterns():
    """Try to find patterns that indicate cert types"""
    print("\n" + "=" * 80)
    print("SEARCHING FOR CERTIFICATION TYPE PATTERNS")
    print("=" * 80)
    
    operators = load_json_file('pay_Operators.txt')
    if not operators:
        return
    
    # Common certification types we might expect
    common_certs = [
        'Driver License', 'Drivers License', 'DL', 
        'Social Security', 'SSN',
        'W9', 'W-9',
        'Background Check', 'BGC',
        'Vehicle Registration', 'Registration',
        'Insurance',
        'Photo ID', 'ID',
        'Vehicle Inspection'
    ]
    
    print("\nLooking for common certification patterns in operator data...")
    
    # Check all fields for these patterns
    operators_sample = operators[:50]  # Check first 50
    found_patterns = defaultdict(list)
    
    for op in operators_sample:
        for field, value in op.items():
            if value and isinstance(value, str):
                for cert in common_certs:
                    if cert.lower() in value.lower():
                        found_patterns[cert].append(f"{field}: {value}")
    
    if found_patterns:
        print("\nFound references to certification types:")
        for cert, examples in found_patterns.items():
            print(f"\n  {cert}:")
            for ex in examples[:3]:  # Show first 3 examples
                print(f"    - {ex}")
    else:
        print("\n  No direct certification type references found in operator fields.")
        print("  This suggests cert types may be in a separate table or encoded differently.")

def main():
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "CERTIFICATION TYPE ANALYSIS" + " " * 31 + "║")
    print("║" + " " * 21 + "From Local Data Files" + " " * 36 + "║")
    print("╚" + "=" * 78 + "╝")
    
    analyze_operators()
    analyze_status_types()
    look_for_cert_type_patterns()
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nNEXT STEPS:")
    print("  1. If certification fields found: Map them to specific statuses")
    print("  2. If no specific cert types found: Need database query for pay_CertTypes table")
    print("  3. Consider that cert requirements might be embedded in business logic")
    print("=" * 80)
    print()

if __name__ == '__main__':
    main()
