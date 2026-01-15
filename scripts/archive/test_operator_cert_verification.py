#!/usr/bin/env python3
"""
Test script to verify operator certification counts and requirements
Usage: python test_operator_cert_verification.py
"""

import json
from collections import defaultdict
from datetime import datetime

def load_json_file(filepath):
    """Load and parse JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def analyze_operator_certs(operator_id, operator_name, operators_data, cert_requirements):
    """Analyze certification status for a specific operator"""
    
    # Find the operator
    operator = None
    for op in operators_data:
        if op.get('ID') == operator_id or f"{op.get('FirstName', '')} {op.get('LastName', '')}".strip() == operator_name:
            operator = op
            break
    
    if not operator:
        print(f"❌ Operator not found: {operator_name or operator_id}")
        return None
    
    print(f"\n{'='*80}")
    print(f"OPERATOR: {operator['FirstName']} {operator['LastName']}")
    print(f"ID: {operator['ID']}")
    print(f"Status: {operator.get('StatusName', 'Unknown')}")
    print(f"Division: {operator.get('DivisionID', 'Unknown')}")
    print(f"{'='*80}\n")
    
    # Get operator's certifications
    operator_certs = operator.get('certifications', [])
    print(f"📋 OPERATOR'S CERTIFICATION COUNT: {len(operator_certs)}")
    
    # Count by status
    cert_status_counts = defaultdict(int)
    valid_certs = []
    expired_certs = []
    no_date_certs = []
    
    for cert in operator_certs:
        cert_type = cert.get('CertType', '')
        issue_date = cert.get('IssueDate', '')
        expire_date = cert.get('ExpireDate', '')
        status = cert.get('Status', '0')
        
        if not issue_date and not expire_date:
            no_date_certs.append(cert_type)
        elif expire_date:
            try:
                exp_date = datetime.strptime(expire_date.split()[0], '%Y-%m-%d')
                if exp_date < datetime.now():
                    expired_certs.append(cert_type)
                    cert_status_counts['expired'] += 1
                else:
                    valid_certs.append(cert_type)
                    cert_status_counts['valid'] += 1
            except:
                no_date_certs.append(cert_type)
        else:
            # Has issue date but no expiration
            if issue_date:
                valid_certs.append(cert_type)
                cert_status_counts['valid'] += 1
            else:
                no_date_certs.append(cert_type)
    
    print(f"   ✅ Valid: {cert_status_counts['valid']}")
    print(f"   ⚠️  Expired: {cert_status_counts['expired']}")
    print(f"   📝 No Date/Missing: {len(no_date_certs)}")
    
    # Get all unique required certifications across all statuses
    all_required_certs = set()
    for status_name, status_data in cert_requirements.items():
        divisions = status_data.get('divisions', {})
        for div_id, div_data in divisions.items():
            required = div_data.get('required', [])
            for cert_obj in required:
                cert_name = cert_obj.get('cert', '')
                if cert_name:
                    all_required_certs.add(cert_name)
    
    print(f"\n📊 TOTAL UNIQUE CERTS REQUIRED (ALL STATUSES): {len(all_required_certs)}")
    
    # Check which required certs the operator has
    operator_cert_names = {cert.get('CertType', '') for cert in operator_certs}
    
    has_required = []
    missing_required = []
    
    for req_cert in sorted(all_required_certs):
        # Check for exact match or close match (case-insensitive, trimmed)
        found = False
        for op_cert in operator_cert_names:
            if op_cert.strip().lower() == req_cert.strip().lower():
                found = True
                break
        
        if found:
            has_required.append(req_cert)
        else:
            missing_required.append(req_cert)
    
    print(f"\n✅ OPERATOR HAS: {len(has_required)} of {len(all_required_certs)} required certs")
    print(f"❌ OPERATOR MISSING: {len(missing_required)} required certs")
    
    # Show discrepancy analysis
    print(f"\n🔍 DISCREPANCY ANALYSIS:")
    print(f"   Operator has {len(operator_certs)} total certs")
    print(f"   System requires {len(all_required_certs)} unique certs (across all statuses)")
    print(f"   Operator has {len(has_required)} of the required ones")
    print(f"   Operator missing {len(missing_required)} required ones")
    
    extra_certs = len(operator_certs) - len(has_required)
    print(f"   Operator has {extra_certs} extra/duplicate/non-standard certs")
    
    # List missing certs
    if missing_required:
        print(f"\n❌ MISSING REQUIRED CERTIFICATIONS ({len(missing_required)}):")
        for cert in sorted(missing_required)[:20]:  # Show first 20
            print(f"   - {cert}")
        if len(missing_required) > 20:
            print(f"   ... and {len(missing_required) - 20} more")
    
    # Check for duplicate cert types
    cert_type_counts = defaultdict(int)
    for cert in operator_certs:
        cert_type_counts[cert.get('CertType', '')] += 1
    
    duplicates = {k: v for k, v in cert_type_counts.items() if v > 1}
    if duplicates:
        print(f"\n⚠️  DUPLICATE CERTIFICATION TYPES ({len(duplicates)}):")
        for cert_type, count in sorted(duplicates.items()):
            print(f"   - {cert_type}: {count} instances")
    
    # List operator's certs not in requirements
    extra_cert_names = [cert for cert in operator_cert_names if cert.strip() not in 
                        {req.strip() for req in all_required_certs}]
    if extra_cert_names:
        print(f"\n📎 CERTS NOT IN REQUIREMENTS ({len(extra_cert_names)}):")
        for cert in sorted(extra_cert_names)[:10]:
            print(f"   - {cert}")
        if len(extra_cert_names) > 10:
            print(f"   ... and {len(extra_cert_names) - 10} more")
    
    return {
        'operator': operator,
        'total_certs': len(operator_certs),
        'valid': cert_status_counts['valid'],
        'expired': cert_status_counts['expired'],
        'no_date': len(no_date_certs),
        'required_total': len(all_required_certs),
        'has_required': len(has_required),
        'missing_required': len(missing_required),
        'duplicates': len(duplicates)
    }

def main():
    print("🔍 OPERATOR CERTIFICATION VERIFICATION TEST")
    print("=" * 80)
    
    # Load data files
    print("\n📂 Loading data files...")
    operators = load_json_file('../generated/pay_Operators.json')
    cert_requirements = load_json_file('../generated/cert_requirements_by_status_division.json')
    
    print(f"✅ Loaded {len(operators)} operators")
    print(f"✅ Loaded {len(cert_requirements)} status requirements")
    
    # Test specific operator: Jalan Minney
    print("\n" + "=" * 80)
    print("TEST CASE: Jalan Minney")
    print("=" * 80)
    
    result = analyze_operator_certs(
        operator_id="0D5B99A8-D6A3-4C8E-8053-0AB30DFF0B28",
        operator_name="Jalan Minney",
        operators_data=operators,
        cert_requirements=cert_requirements
    )
    
    # Test another random operator for comparison
    print("\n" + "=" * 80)
    print("TEST CASE: Random Operator (for comparison)")
    print("=" * 80)
    
    if len(operators) > 5:
        random_op = operators[5]
        analyze_operator_certs(
            operator_id=random_op['ID'],
            operator_name=f"{random_op.get('FirstName', '')} {random_op.get('LastName', '')}",
            operators_data=operators,
            cert_requirements=cert_requirements
        )
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
