#!/usr/bin/env python3
"""
Extract actual certification types from the certifications data
and map them to operators and their statuses
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

def analyze_certification_types():
    """Extract all unique certification types from certifications data"""
    print("=" * 80)
    print("EXTRACTING CERTIFICATION TYPES")
    print("=" * 80)
    
    certifications = load_json_file('pay_Certifications.txt')
    if not certifications:
        return {}
    
    print(f"\nTotal certification records: {len(certifications)}")
    
    # Extract unique cert types
    cert_types = {}  # CertTypeID -> Cert Name
    cert_type_counts = Counter()
    
    for cert in certifications:
        if not cert.get('IsDeleted', False):  # Only active certs
            cert_type_id = cert.get('CertTypeID')
            cert_name = cert.get('Cert')
            
            if cert_name:
                cert_name = cert_name.strip()
            else:
                cert_name = ''
            
            if cert_type_id and cert_name:
                cert_types[cert_type_id] = cert_name
                cert_type_counts[cert_name] += 1
    
    print(f"\nUnique certification types found: {len(cert_types)}")
    print("\n" + "=" * 80)
    print("ALL CERTIFICATION TYPES (sorted by usage):")
    print("=" * 80)
    
    for cert_name, count in cert_type_counts.most_common():
        print(f"  {cert_name:<50} ({count:>4} records)")
    
    return cert_types

def map_certs_to_operators():
    """Map which certifications each operator has"""
    print("\n" + "=" * 80)
    print("MAPPING CERTIFICATIONS TO OPERATORS")
    print("=" * 80)
    
    certifications = load_json_file('pay_Certifications.txt')
    operators = load_json_file('pay_Operators.txt')
    
    if not certifications or not operators:
        return
    
    # Create operator lookup
    operator_map = {op['Id']: op for op in operators}
    
    # Map operator -> list of certs
    operator_certs = defaultdict(list)
    
    for cert in certifications:
        if not cert.get('IsDeleted', False):
            op_id = cert.get('OperatorID')
            cert_name = cert.get('Cert')
            if cert_name:
                cert_name = cert_name.strip()
            else:
                cert_name = ''
            
            if op_id and cert_name and op_id in operator_map:
                operator_certs[op_id].append({
                    'cert': cert_name,
                    'approved': cert.get('isApproved', False),
                    'reviewed': cert.get('isReviewed', False)
                })
    
    print(f"\nOperators with certifications: {len(operator_certs)} / {len(operators)}")
    
    # Group by division and status
    division_status_certs = defaultdict(lambda: defaultdict(Counter))
    
    for op_id, certs in operator_certs.items():
        operator = operator_map[op_id]
        division = operator.get('DivisionID', 'Unknown')
        status = operator.get('CurrentStatus', 'Unknown')
        
        for cert_info in certs:
            division_status_certs[division][status][cert_info['cert']] += 1
    
    # Focus on target divisions
    target_divs = ['2 - IL', '3 - TX', '5 - CA', '6 - FL', '7 - MI', '8 - OH', '10 - OR', '11 - GA', '12 - PA']
    excluded_divs = ['PA - BROOKES', '2 - LAHORE']  # Divisions to exclude from analysis
    
    print("\n" + "=" * 80)
    print("CERTIFICATIONS BY DIVISION AND STATUS")
    print("=" * 80)
    
    for div_prefix in target_divs:
        matching_divs = [d for d in division_status_certs.keys() if d.startswith(div_prefix)]
        
        if matching_divs:
            print(f"\n{'='*80}")
            print(f"{div_prefix}")
            print(f"{'='*80}")
            
            for div in matching_divs:
                statuses = division_status_certs[div]
                
                for status in sorted(statuses.keys()):
                    certs = statuses[status]
                    
                    if certs:
                        print(f"\n  Status: {status}")
                        for cert_name, count in certs.most_common(10):  # Top 10 certs per status
                            print(f"    • {cert_name:<45} ({count} operators)")

def identify_registration_onboarding_certs():
    """Specifically look at Registration and Onboarding certifications"""
    print("\n" + "=" * 80)
    print("REGISTRATION & ONBOARDING CERTIFICATIONS")
    print("=" * 80)
    
    certifications = load_json_file('pay_Certifications.txt')
    operators = load_json_file('pay_Operators.txt')
    
    if not certifications or not operators:
        return
    
    # Create operator lookup
    operator_map = {op['Id']: op for op in operators}
    
    # Find certs for registration/onboarding
    reg_onboard_certs = defaultdict(Counter)
    
    for cert in certifications:
        if not cert.get('IsDeleted', False):
            op_id = cert.get('OperatorID')
            cert_name = cert.get('Cert')
            if cert_name:
                cert_name = cert_name.strip()
            else:
                cert_name = ''
            
            if op_id and cert_name and op_id in operator_map:
                operator = operator_map[op_id]
                status = operator.get('CurrentStatus', '').upper()
                
                if 'REGISTRATION' in status or 'ONBOARDING' in status:
                    reg_onboard_certs[status][cert_name] += 1
    
    for status in sorted(reg_onboard_certs.keys()):
        print(f"\n{status}:")
        for cert_name, count in reg_onboard_certs[status].most_common():
            print(f"  • {cert_name:<50} ({count} operators)")

def main():
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 18 + "ACTUAL CERTIFICATION ANALYSIS" + " " * 29 + "║")
    print("║" + " " * 23 + "Based on Real Data" + " " * 36 + "║")
    print("╚" + "=" * 78 + "╝")
    
    cert_types = analyze_certification_types()
    map_certs_to_operators()
    identify_registration_onboarding_certs()
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print()

if __name__ == '__main__':
    main()