#!/usr/bin/env python3
"""
Deep dive analysis of operator certification data
Focus on operator 0D5B99A8-D6A3-4C8E-8053-0AB30DFF0B28 (Jalan Minney)
"""

import json
from collections import defaultdict
from datetime import datetime
from difflib import SequenceMatcher

def load_json_file(filepath):
    """Load and parse JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def similar(a, b):
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()

def normalize_cert_name(name):
    """Normalize certification name for comparison"""
    return name.lower().strip().replace('  ', ' ')

def analyze_operator_deep_dive(operator_id, operators_data, cert_requirements):
    """Deep dive analysis of a specific operator"""
    
    # Find the operator
    operator = None
    for op in operators_data:
        if op.get('ID') == operator_id:
            operator = op
            break
    
    if not operator:
        print(f"❌ Operator not found: {operator_id}")
        return
    
    print(f"\n{'='*100}")
    print(f"DEEP DIVE ANALYSIS: {operator['FirstName']} {operator['LastName']}")
    print(f"{'='*100}")
    print(f"ID: {operator['ID']}")
    print(f"Status: {operator.get('StatusName', 'Unknown')}")
    print(f"Division: {operator.get('DivisionID', 'Unknown')}")
    print(f"Email: {operator.get('Email', 'N/A')}")
    print(f"{'='*100}\n")
    
    # Get division ID (full format like "10 - OR")
    division_id = operator.get('DivisionID', '')
    
    # Get operator's certifications
    operator_certs = operator.get('certifications', [])
    
    print(f"📋 OPERATOR'S CERTIFICATION RECORDS: {len(operator_certs)}")
    print(f"{'='*100}\n")
    
    # Analyze each cert
    valid_certs = []
    expired_certs = []
    no_date_certs = []
    
    cert_details = []
    
    for idx, cert in enumerate(operator_certs, 1):
        cert_type = cert.get('CertType', '')
        issue_date = cert.get('IssueDate', '')
        expire_date = cert.get('ExpireDate', '')
        status = cert.get('Status', '0')
        cert_id = cert.get('CertificationID', '')
        
        # Determine status - MUST be approved (Status != '0') AND have dates
        is_approved = status != '0' and (issue_date or expire_date)
        
        if not is_approved:
            cert_status = 'NOT_APPROVED'
            no_date_certs.append(cert_type)
        elif expire_date:
            try:
                exp_date = datetime.strptime(expire_date.split()[0], '%Y-%m-%d')
                if exp_date < datetime.now():
                    cert_status = 'EXPIRED'
                    expired_certs.append(cert_type)
                else:
                    cert_status = 'VALID'
                    valid_certs.append(cert_type)
            except:
                cert_status = 'NOT_APPROVED'
                no_date_certs.append(cert_type)
        elif issue_date:
            # Has issue date but no expiration - consider valid if approved
            cert_status = 'VALID'
            valid_certs.append(cert_type)
        else:
            cert_status = 'NOT_APPROVED'
            no_date_certs.append(cert_type)
        
        cert_details.append({
            'index': idx,
            'name': cert_type,
            'status': cert_status,
            'issue_date': issue_date,
            'expire_date': expire_date,
            'cert_id': cert_id
        })
    
    print(f"CERTIFICATION STATUS BREAKDOWN:")
    print(f"   ✅ Valid (Approved + Not Expired): {len(valid_certs)}")
    print(f"   ⚠️  Expired (Approved but Expired): {len(expired_certs)}")
    print(f"   📝 Not Approved (Status='0' or no dates): {len(no_date_certs)}")
    print(f"\n{'='*100}\n")
    
    # Show all certs
    print(f"DETAILED CERTIFICATION LIST:")
    print(f"{'-'*100}")
    for cert in cert_details:
        status_map = {'VALID': '✅', 'EXPIRED': '⚠️', 'NOT_APPROVED': '📝'}
        status_icon = status_map.get(cert['status'], '❓')
        print(f"{cert['index']:3}. {status_icon} {cert['name']:<50} [{cert['status']}]")
        if cert['issue_date'] or cert['expire_date']:
            print(f"      Issue: {cert['issue_date'] or 'N/A':<20} Expire: {cert['expire_date'] or 'N/A'}")
    print(f"{'-'*100}\n")
    
    # Get requirements for operator's specific division and status
    print(f"\n{'='*100}")
    print(f"REQUIREMENTS FOR DIVISION {division_id}")
    print(f"{'='*100}\n")
    
    status_name = operator.get('StatusName', '')
    
    # Get requirements for this specific division across all statuses
    division_requirements = {}
    all_division_certs = set()
    
    for status, status_data in cert_requirements.items():
        divisions = status_data.get('divisions', {})
        if division_id in divisions:
            required = divisions[division_id].get('required', [])
            division_requirements[status] = [cert.get('cert', '') for cert in required]
            all_division_certs.update(division_requirements[status])
    
    print(f"📊 TOTAL UNIQUE CERTS REQUIRED FOR DIVISION {division_id}: {len(all_division_certs)}")
    print(f"\nBreakdown by Status:")
    for status, certs in sorted(division_requirements.items()):
        print(f"   {status}: {len(certs)} certs")
    
    # Get requirements for current status
    current_status_reqs = division_requirements.get(status_name, [])
    print(f"\n🎯 CERTS REQUIRED FOR CURRENT STATUS ({status_name}): {len(current_status_reqs)}")
    
    # Match operator certs to division requirements
    print(f"\n{'='*100}")
    print(f"MATCHING ANALYSIS: OPERATOR CERTS vs DIVISION {division_id} REQUIREMENTS")
    print(f"{'='*100}\n")
    
    operator_cert_names = {normalize_cert_name(cert['name']) for cert in cert_details}
    required_cert_names = {normalize_cert_name(cert) for cert in all_division_certs}
    
    # Find exact matches
    exact_matches = []
    fuzzy_matches = []
    missing_certs = []
    extra_certs = []
    
    for req_cert in sorted(all_division_certs):
        req_norm = normalize_cert_name(req_cert)
        
        # Check for exact match
        if req_norm in operator_cert_names:
            exact_matches.append(req_cert)
        else:
            # Check for fuzzy match
            best_match = None
            best_score = 0
            for op_cert in cert_details:
                score = similar(req_cert, op_cert['name'])
                if score > best_score:
                    best_score = score
                    best_match = op_cert['name']
            
            if best_score > 0.85:  # 85% similarity
                fuzzy_matches.append({
                    'required': req_cert,
                    'operator_has': best_match,
                    'similarity': best_score
                })
            else:
                missing_certs.append(req_cert)
    
    # Find certs operator has that aren't required
    for op_cert in cert_details:
        op_norm = normalize_cert_name(op_cert['name'])
        if op_norm not in required_cert_names:
            # Check if it's a fuzzy match
            is_fuzzy = any(fm['operator_has'] == op_cert['name'] for fm in fuzzy_matches)
            if not is_fuzzy:
                extra_certs.append(op_cert['name'])
    
    print(f"✅ EXACT MATCHES: {len(exact_matches)}")
    print(f"🔄 FUZZY MATCHES (likely naming variations): {len(fuzzy_matches)}")
    print(f"❌ MISSING (required but not found): {len(missing_certs)}")
    print(f"📎 EXTRA (operator has but not required for division): {len(extra_certs)}")
    
    print(f"\n{'='*100}")
    print(f"EXACT MATCHES ({len(exact_matches)}):")
    print(f"{'-'*100}")
    for cert in sorted(exact_matches)[:20]:
        print(f"   ✅ {cert}")
    if len(exact_matches) > 20:
        print(f"   ... and {len(exact_matches) - 20} more")
    
    if fuzzy_matches:
        print(f"\n{'='*100}")
        print(f"FUZZY MATCHES (NAMING DISCREPANCIES):")
        print(f"{'-'*100}")
        for fm in sorted(fuzzy_matches, key=lambda x: x['similarity'], reverse=True):
            print(f"   🔄 Required: '{fm['required']}'")
            print(f"      Operator has: '{fm['operator_has']}'")
            print(f"      Similarity: {fm['similarity']*100:.1f}%")
            print()
    
    if missing_certs:
        print(f"\n{'='*100}")
        print(f"MISSING CERTIFICATIONS ({len(missing_certs)}):")
        print(f"{'-'*100}")
        for cert in sorted(missing_certs)[:20]:
            print(f"   ❌ {cert}")
        if len(missing_certs) > 20:
            print(f"   ... and {len(missing_certs) - 20} more")
    
    if extra_certs:
        print(f"\n{'='*100}")
        print(f"EXTRA/NON-STANDARD CERTIFICATIONS ({len(extra_certs)}):")
        print(f"{'-'*100}")
        for cert in sorted(set(extra_certs))[:20]:
            print(f"   📎 {cert}")
        if len(set(extra_certs)) > 20:
            print(f"   ... and {len(set(extra_certs)) - 20} more")
    
    # Analyze naming inconsistencies across divisions
    print(f"\n{'='*100}")
    print(f"NAMING INCONSISTENCY ANALYSIS ACROSS ALL DIVISIONS")
    print(f"{'='*100}\n")
    
    # Collect all cert names from all divisions and statuses
    all_cert_names = defaultdict(lambda: {'statuses': set(), 'divisions': set(), 'variations': set()})
    
    for status, status_data in cert_requirements.items():
        divisions = status_data.get('divisions', {})
        for div_id, div_data in divisions.items():
            required = div_data.get('required', [])
            for cert_obj in required:
                cert_name = cert_obj.get('cert', '')
                norm_name = normalize_cert_name(cert_name)
                all_cert_names[norm_name]['statuses'].add(status)
                all_cert_names[norm_name]['divisions'].add(div_id)
                all_cert_names[norm_name]['variations'].add(cert_name)
    
    # Find certs with multiple name variations
    print(f"CERTIFICATION NAME VARIATIONS (Same cert, different spellings/formatting):")
    print(f"{'-'*100}")
    
    variations_found = []
    for norm_name, data in all_cert_names.items():
        if len(data['variations']) > 1:
            variations_found.append({
                'normalized': norm_name,
                'variations': sorted(data['variations']),
                'count': len(data['variations']),
                'divisions': sorted(data['divisions']),
                'statuses': sorted(data['statuses'])
            })
    
    for var in sorted(variations_found, key=lambda x: x['count'], reverse=True)[:30]:
        print(f"\n🔍 Base Name: {var['normalized']}")
        print(f"   Found in {len(var['divisions'])} divisions, {len(var['statuses'])} statuses")
        print(f"   {var['count']} variations:")
        for v in var['variations']:
            print(f"      - '{v}'")
    
    if len(variations_found) > 30:
        print(f"\n... and {len(variations_found) - 30} more certification types with variations")
    
    # Summary
    print(f"\n{'='*100}")
    print(f"SUMMARY")
    print(f"{'='*100}")
    print(f"\nOperator: {operator['FirstName']} {operator['LastName']} (Division {division_id})")
    print(f"Total Cert Records: {len(operator_certs)}")
    print(f"   ✅ Valid/Approved: {len(valid_certs)}")
    print(f"   ⚠️  Expired: {len(expired_certs)}")
    print(f"   📝 Not Approved (no dates): {len(no_date_certs)}")
    print(f"\nDivision {division_num} Requirements: {len(all_division_certs)} unique certs")
    print(f"   ✅ Exact matches: {len(exact_matches)}")
    print(f"   🔄 Fuzzy matches: {len(fuzzy_matches)}")
    print(f"   ❌ Missing: {len(missing_certs)}")
    print(f"   📎 Extra/non-standard: {len(set(extra_certs))}")
    print(f"\nNaming Issues Found: {len(variations_found)} cert types have multiple name variations")
    
    completion_rate = ((len(exact_matches) + len(fuzzy_matches)) / len(all_division_certs) * 100) if all_division_certs else 0
    print(f"\n📊 Completion Rate for Division {division_num}: {completion_rate:.1f}%")
    
    # The "33 approved certs" question
    total_approved = len(exact_matches) + len(fuzzy_matches)
    print(f"\n🎯 ANSWER TO YOUR QUESTION:")
    print(f"   This operator has {total_approved} certs that match division requirements")
    print(f"   ({len(exact_matches)} exact + {len(fuzzy_matches)} fuzzy matches)")
    print(f"   All {len(no_date_certs)} certs currently show NO approval dates (Status='0')")
    print(f"   So technically, 0 are 'approved' (have dates), but {total_approved} match required names")

def main():
    print("🔍 DEEP DIVE OPERATOR CERTIFICATION ANALYSIS")
    print("=" * 100)
    
    # Load data files
    print("\n📂 Loading data files...")
    operators = load_json_file('../generated/pay_Operators.json')
    cert_requirements = load_json_file('../generated/cert_requirements_by_status_division.json')
    
    print(f"✅ Loaded {len(operators)} operators")
    print(f"✅ Loaded {len(cert_requirements)} status requirements")
    
    # Deep dive on Jalan Minney
    analyze_operator_deep_dive(
        operator_id="0D5B99A8-D6A3-4C8E-8053-0AB30DFF0B28",
        operators_data=operators,
        cert_requirements=cert_requirements
    )
    
    print(f"\n{'='*100}")
    print("✅ ANALYSIS COMPLETE")
    print("=" * 100)

if __name__ == '__main__':
    main()
