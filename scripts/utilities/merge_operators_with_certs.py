#!/usr/bin/env python3
"""
Merge operators with their certifications for the workflow builder
"""

import json
from pathlib import Path
from collections import defaultdict

def main():
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / 'data'
    generated_dir = base_dir / 'generated'
    
    print("Loading operators...")
    with open(data_dir / 'pay_Operators.json', 'r') as f:
        operators = json.load(f)
    
    print(f"✓ Loaded {len(operators)} operators")
    
    print("\nLoading certifications...")
    with open(data_dir / 'pay_Certifications.json', 'r') as f:
        cert_data = json.load(f)
    
    # Handle both array and object with 'certifications' key
    if isinstance(cert_data, dict) and 'certifications' in cert_data:
        certifications = cert_data['certifications']
    else:
        certifications = cert_data
    
    print(f"✓ Loaded {len(certifications)} certification records")
    
    # Group certifications by operator ID
    print("\nGrouping certifications by operator...")
    certs_by_operator = defaultdict(list)
    for cert in certifications:
        operator_id = cert.get('OperatorID')
        if operator_id:
            certs_by_operator[operator_id].append({
                'CertType': cert.get('Cert', 'Unknown'),
                'IssueDate': cert.get('CompletionDate'),  # CompletionDate is when cert was obtained
                'ExpireDate': cert.get('Date'),            # Date is the expiration date
                'Status': cert.get('isApproved'),
                'CertificationID': cert.get('CertificationID')
            })
    
    print(f"✓ Grouped certifications for {len(certs_by_operator)} operators")
    
    # Merge certifications into operators
    print("\nMerging data...")
    for operator in operators:
        operator_id = operator.get('ID')
        operator['certifications'] = certs_by_operator.get(operator_id, [])
    
    # Save merged data
    output_file = generated_dir / 'pay_Operators.json'
    print(f"\nSaving merged data to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(operators, f, indent=2)
    
    print(f"\n✓ Success!")
    print(f"✓ {len(operators)} operators with certifications saved")
    
    # Print summary
    operators_with_certs = sum(1 for op in operators if op['certifications'])
    print(f"\nSummary:")
    print(f"  - Operators with certifications: {operators_with_certs}")
    print(f"  - Operators without certifications: {len(operators) - operators_with_certs}")
    print(f"  - Total certification records: {sum(len(op['certifications']) for op in operators)}")

if __name__ == '__main__':
    main()
