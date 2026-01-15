#!/usr/bin/env python3
"""
Analyze certification name matching issues across divisions
Specifically investigate cases where operator has cert but doesn't match requirements
Example: Operator has "CTAA PASSENGER ASSISTANCE" but needs "CTAA Passenger Assistance"
"""

import json
from collections import defaultdict
from difflib import SequenceMatcher

def normalize_cert_name(name):
    """Normalize certification name for fuzzy matching"""
    return name.lower().strip().replace('  ', ' ')

def load_json_file(filepath):
    """Load and parse JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def find_operator_by_name(operators, search_name):
    """Find operator by partial name match"""
    search_lower = search_name.lower()
    matches = []
    for op in operators:
        full_name = f"{op.get('FirstName', '')} {op.get('LastName', '')}".lower()
        if search_lower in full_name or full_name in search_lower:
            matches.append(op)
    return matches

def analyze_cert_name_mismatch(operator_id=None, operator_name=None, operators_data=None, cert_requirements=None):
    """Analyze why operator's cert doesn't match requirements"""
    
    # Find operator
    if operator_id:
        operator = next((op for op in operators_data if op.get('ID') == operator_id), None)
    elif operator_name:
        matches = find_operator_by_name(operators_data, operator_name)
        if len(matches) == 0:
            print(f"❌ No operator found matching: {operator_name}")
            return
        elif len(matches) > 1:
            print(f"⚠️  Multiple operators found matching '{operator_name}':")
            for i, op in enumerate(matches, 1):
                print(f"   {i}. {op.get('FirstName')} {op.get('LastName')} - Division {op.get('DivisionID')}")
            return
        operator = matches[0]
    else:
        print("❌ Must provide either operator_id or operator_name")
        return
    
    print(f"\n{'='*100}")
    print(f"CERTIFICATION NAME MISMATCH ANALYSIS")
    print(f"{'='*100}")
    print(f"Operator: {operator.get('FirstName')} {operator.get('LastName')}")
    print(f"ID: {operator.get('ID')}")
    print(f"Division: {operator.get('DivisionID')}")
    print(f"Status: {operator.get('StatusName')}")
    print(f"{'='*100}\n")
    
    # Get operator's division
    division_id = operator.get('DivisionID', '')
    division_num = division_id.split(' ')[0] if division_id else None
    
    # Get operator's certs
    operator_certs = operator.get('certifications', [])
    operator_cert_names = {cert.get('CertType', ''): cert for cert in operator_certs}
    
    print(f"Operator has {len(operator_certs)} certification records\n")
    
    # Get ALL required certs across all statuses for this division
    division_required_certs = {}  # cert_name -> [statuses that require it]
    
    for status_name, status_data in cert_requirements.items():
        divisions = status_data.get('divisions', {})
        if division_num in divisions:
            div_data = divisions[division_num]
            required = div_data.get('required', [])
            for cert_obj in required:
                cert_name = cert_obj.get('cert', '')
                if cert_name not in division_required_certs:
                    division_required_certs[cert_name] = []
                division_required_certs[cert_name].append(status_name)
    
    print(f"Division {division_num} requires {len(division_required_certs)} unique certifications\n")
    
    # Find mismatches - operator has cert but doesn't exactly match requirements
    print(f"{'='*100}")
    print(f"ANALYZING NAMING MISMATCHES")
    print(f"{'='*100}\n")
    
    mismatches = []
    
    for required_cert, statuses in sorted(division_required_certs.items()):
        # Check exact match first
        if required_cert in operator_cert_names:
            continue  # Perfect match, no issue
        
        # Check normalized match
        required_norm = normalize_cert_name(required_cert)
        
        for op_cert_name, op_cert_data in operator_cert_names.items():
            op_norm = normalize_cert_name(op_cert_name)
            
            if required_norm == op_norm:
                # Normalized match but not exact - this is the issue!
                mismatches.append({
                    'required': required_cert,
                    'operator_has': op_cert_name,
                    'statuses': statuses,
                    'operator_cert_data': op_cert_data,
                    'match_type': 'NORMALIZED_MATCH'
                })
                break
            
            # Check high similarity (90%+)
            similarity = SequenceMatcher(None, required_norm, op_norm).ratio()
            if similarity > 0.90:
                mismatches.append({
                    'required': required_cert,
                    'operator_has': op_cert_name,
                    'statuses': statuses,
                    'operator_cert_data': op_cert_data,
                    'similarity': similarity,
                    'match_type': 'FUZZY_MATCH'
                })
                break
    
    if not mismatches:
        print("✅ No naming mismatches found! All operator certs match requirements exactly.\n")
        return
    
    print(f"🔍 FOUND {len(mismatches)} NAMING MISMATCH(ES):\n")
    
    for idx, mismatch in enumerate(mismatches, 1):
        print(f"{idx}. MISMATCH DETECTED:")
        print(f"   {'─'*96}")
        print(f"   Required (in cert_requirements): '{mismatch['required']}'")
        print(f"   Operator Has (in pay_Operators):  '{mismatch['operator_has']}'")
        print(f"   Match Type: {mismatch['match_type']}")
        if 'similarity' in mismatch:
            print(f"   Similarity: {mismatch['similarity']*100:.1f}%")
        print(f"\n   Required for statuses: {', '.join(mismatch['statuses'])}")
        
        # Character-by-character comparison
        req = mismatch['required']
        has = mismatch['operator_has']
        
        print(f"\n   CHARACTER COMPARISON:")
        print(f"   Required: ", end="")
        for i, char in enumerate(req):
            if i < len(has) and req[i] == has[i]:
                print(char, end="")
            else:
                print(f"\033[91m{char}\033[0m", end="")  # Red for differences
        print(f" (len={len(req)})")
        
        print(f"   Has:      ", end="")
        for i, char in enumerate(has):
            if i < len(req) and req[i] == has[i]:
                print(char, end="")
            else:
                print(f"\033[91m{char}\033[0m", end="")  # Red for differences
        print(f" (len={len(has)})")
        
        # Show differences
        print(f"\n   DIFFERENCES:")
        if req.lower() == has.lower():
            print(f"   - CASE ONLY: Requirements use different capitalization")
        if req.strip() != req or has.strip() != has:
            print(f"   - WHITESPACE: Leading/trailing spaces detected")
        if '  ' in req or '  ' in has:
            print(f"   - DOUBLE SPACES: Multiple consecutive spaces found")
        if req.rstrip() != req or has.rstrip() != has:
            print(f"   - TRAILING SPACE: Invisible space at end")
        
        # Show cert details
        cert_data = mismatch['operator_cert_data']
        print(f"\n   OPERATOR'S CERT DETAILS:")
        print(f"   - Status: {cert_data.get('Status', 'N/A')}")
        print(f"   - Issue Date: {cert_data.get('IssueDate', 'N/A')}")
        print(f"   - Expire Date: {cert_data.get('ExpireDate', 'N/A')}")
        print(f"   - ID: {cert_data.get('CertificationID', 'N/A')}")
        
        print()
    
    # Check if requirements have variations within same division
    print(f"\n{'='*100}")
    print(f"CHECKING FOR VARIATIONS IN REQUIREMENTS (SAME DIVISION)")
    print(f"{'='*100}\n")
    
    # Group by normalized name to find variations
    cert_variations = defaultdict(lambda: {'names': set(), 'statuses': {}})
    
    for status_name, status_data in cert_requirements.items():
        divisions = status_data.get('divisions', {})
        if division_num in divisions:
            div_data = divisions[division_num]
            required = div_data.get('required', [])
            for cert_obj in required:
                cert_name = cert_obj.get('cert', '')
                norm_name = normalize_cert_name(cert_name)
                cert_variations[norm_name]['names'].add(cert_name)
                if cert_name not in cert_variations[norm_name]['statuses']:
                    cert_variations[norm_name]['statuses'][cert_name] = []
                cert_variations[norm_name]['statuses'][cert_name].append(status_name)
    
    variations_found = {k: v for k, v in cert_variations.items() if len(v['names']) > 1}
    
    if variations_found:
        print(f"⚠️  FOUND {len(variations_found)} CERT(S) WITH MULTIPLE NAME FORMATS IN DIVISION {division_num}:\n")
        
        for norm_name, data in sorted(variations_found.items()):
            print(f"Cert: {norm_name} ({len(data['names'])} variations)")
            for name in sorted(data['names']):
                statuses = data['statuses'].get(name, [])
                print(f"   - '{name}' (used in: {', '.join(statuses)})")
            print()
    else:
        print(f"✅ No variations found within Division {division_num} requirements\n")
    
    # Recommendations
    print(f"\n{'='*100}")
    print(f"RECOMMENDATIONS")
    print(f"{'='*100}\n")
    
    print(f"1. IMMEDIATE FIX - Update Requirements File:")
    print(f"   Standardize all cert names in cert_requirements_by_status_division.json")
    print(f"   Choose one canonical format and update all instances\n")
    
    print(f"2. OR - Implement Fuzzy Matching:")
    print(f"   Update validation logic to normalize names before comparison")
    print(f"   Treat 'CTAA PASSENGER ASSISTANCE' same as 'CTAA Passenger Assistance'\n")
    
    print(f"3. LONG-TERM - Create Canonical Reference:")
    print(f"   Maintain master list of certification types with canonical names")
    print(f"   Map all variations to canonical name")
    print(f"   Update data entry to prevent new variations\n")

def main():
    print("🔍 CERTIFICATION NAME MISMATCH ANALYZER")
    print("=" * 100)
    
    # Load data
    print("\n📂 Loading data files...")
    operators = load_json_file('../generated/pay_Operators.json')
    cert_requirements = load_json_file('../generated/cert_requirements_by_status_division.json')
    
    print(f"✅ Loaded {len(operators)} operators")
    print(f"✅ Loaded {len(cert_requirements)} status requirements")
    
    # Analyze Willie Quainton (or whoever the user mentioned)
    print("\n" + "=" * 100)
    print("SEARCHING FOR OPERATOR...")
    print("=" * 100)
    
    # Try to find Willie Quainton
    matches = find_operator_by_name(operators, "willie quainton")
    
    if not matches:
        print("\n⚠️  Willie Quainton not found. Testing with first operator in REGISTRATION...")
        # Find first operator in REGISTRATION with some certs
        for op in operators:
            if op.get('StatusName') == 'REGISTRATION' and op.get('certifications'):
                analyze_cert_name_mismatch(
                    operator_id=op['ID'],
                    operators_data=operators,
                    cert_requirements=cert_requirements
                )
                break
    else:
        analyze_cert_name_mismatch(
            operator_id=matches[0]['ID'],
            operators_data=operators,
            cert_requirements=cert_requirements
        )
    
    # Analyze ALL operators for mismatch statistics
    print(f"\n\n{'='*100}")
    print(f"SYSTEM-WIDE MISMATCH STATISTICS")
    print(f"{'='*100}\n")
    
    total_operators = len(operators)
    operators_with_mismatches = 0
    total_mismatches = 0
    mismatch_by_cert = defaultdict(int)
    
    for operator in operators:
        division_id = operator.get('DivisionID', '')
        division_num = division_id.split(' ')[0] if division_id else None
        
        if not division_num:
            continue
        
        operator_cert_names = {cert.get('CertType', '') for cert in operator.get('certifications', [])}
        
        # Get required certs for this division
        division_required = set()
        for status_name, status_data in cert_requirements.items():
            divisions = status_data.get('divisions', {})
            if division_num in divisions:
                required = divisions[division_num].get('required', [])
                for cert_obj in required:
                    division_required.add(cert_obj.get('cert', ''))
        
        # Find mismatches
        operator_has_mismatch = False
        for required_cert in division_required:
            if required_cert in operator_cert_names:
                continue
            
            required_norm = normalize_cert_name(required_cert)
            for op_cert in operator_cert_names:
                op_norm = normalize_cert_name(op_cert)
                if required_norm == op_norm:
                    operator_has_mismatch = True
                    total_mismatches += 1
                    mismatch_by_cert[required_cert] += 1
                    break
        
        if operator_has_mismatch:
            operators_with_mismatches += 1
    
    print(f"Total Operators: {total_operators}")
    print(f"Operators Affected by Name Mismatches: {operators_with_mismatches} ({operators_with_mismatches/total_operators*100:.1f}%)")
    print(f"Total Mismatches Found: {total_mismatches}")
    
    if mismatch_by_cert:
        print(f"\nTop 10 Certifications with Naming Issues:")
        for cert_name, count in sorted(mismatch_by_cert.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {count:3d}x - {cert_name}")
    
    print(f"\n{'='*100}")
    print("✅ ANALYSIS COMPLETE")
    print("=" * 100)

if __name__ == '__main__':
    main()
