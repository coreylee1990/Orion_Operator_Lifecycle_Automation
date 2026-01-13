#!/usr/bin/env python3
"""
Generate Pizza Status Requirements from Inference

This script analyzes actual operator data, groups by PizzaStatusID,
and infers required certifications using an 80% threshold.

Output: data/pay_PizzaStatusRequirements.json
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set

# Divisions to exclude from analysis
EXCLUDED_DIVS = ['PA - BROOKES', '2 - LAHORE']

# Threshold for determining if cert is required
REQUIREMENT_THRESHOLD = 0.80  # 80%

def load_json_data(file_path: Path):
    """Load JSON data from file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize_cert_name(cert_name: str, aliases: Dict) -> str:
    """Normalize certification name using aliases."""
    cert_lower = cert_name.strip().lower()
    
    for canonical, variations in aliases.items():
        for variation in variations:
            if cert_lower == variation.lower():
                return canonical
    
    return cert_name.strip()

def get_pizza_status_id(operator: Dict, status_types: List[Dict]) -> str:
    """Get the PizzaStatusID for an operator based on their status and division."""
    status = operator.get('StatusName', '') or operator.get('CurrentStatus', '')
    division = operator.get('DivisionID', '')
    
    for st in status_types:
        if st['Status'] == status and st['DivisionID'] == division:
            return st.get('PizzaStatusID', '')
    
    return ''

def group_operators_by_pizza_status(operators: List[Dict], status_types: List[Dict]) -> Dict:
    """Group operators by their PizzaStatusID."""
    pizza_groups = defaultdict(list)
    
    for operator in operators:
        # Skip excluded divisions
        division = operator.get('DivisionID', '')
        if any(excluded in division for excluded in EXCLUDED_DIVS):
            continue
        
        pizza_id = get_pizza_status_id(operator, status_types)
        if pizza_id:
            pizza_groups[pizza_id].append(operator)
    
    return dict(pizza_groups)

def get_operator_certifications(operator_id: str, certifications: Dict, aliases: Dict) -> Set[str]:
    """Get all approved, non-deleted certifications for an operator."""
    certs = set()
    
    # Check if certifications is a dict keyed by operator ID or a list
    if isinstance(certifications, dict):
        # Certifications organized by operator ID
        operator_certs_list = certifications.get(operator_id, [])
        if not isinstance(operator_certs_list, list):
            operator_certs_list = [operator_certs_list]
        
        for cert in operator_certs_list:
            is_approved = str(cert.get('isApproved', '0')) == '1'
            is_deleted = str(cert.get('IsDeleted', '0')) == '0'
            
            if is_approved and is_deleted:
                cert_name = cert.get('Cert') or cert.get('Name')
                if cert_name:
                    normalized = normalize_cert_name(cert_name, aliases)
                    certs.add(normalized)
    else:
        # Certifications as flat list
        for cert in certifications:
            cert_operator_id = cert.get('ID') or cert.get('OperatorID')
            if cert_operator_id == operator_id:
                is_approved = str(cert.get('isApproved', '0')) == '1'
                is_deleted = str(cert.get('IsDeleted', '0')) == '0'
                
                if is_approved and is_deleted:
                    cert_name = cert.get('Cert') or cert.get('Name')
                    if cert_name:
                        normalized = normalize_cert_name(cert_name, aliases)
                        certs.add(normalized)
    
    return certs

def infer_requirements_for_pizza_status(
    operators: List[Dict],
    certifications: List[Dict],
    aliases: Dict,
    threshold: float = 0.80
) -> Dict:
    """
    Infer required certifications for a pizza status group.
    Returns dict with cert names and their coverage percentages.
    """
    if not operators:
        return {}
    
    total_operators = len(operators)
    cert_counts = defaultdict(int)
    
    # Count how many operators have each cert
    for operator in operators:
        operator_id = operator.get('Id') or operator.get('ID')
        if not operator_id:
            continue
        
        operator_certs = get_operator_certifications(operator_id, certifications, aliases)
        for cert_name in operator_certs:
            cert_counts[cert_name] += 1
    
    # Calculate coverage percentages
    cert_coverage = {}
    for cert_name, count in cert_counts.items():
        percentage = count / total_operators
        if percentage >= threshold:
            cert_coverage[cert_name] = {
                'count': count,
                'total': total_operators,
                'percentage': round(percentage * 100, 1)
            }
    
    return cert_coverage

def get_pizza_status_info(pizza_id: str, pizza_statuses: List[Dict]) -> Dict:
    """Get information about a pizza status."""
    for ps in pizza_statuses:
        if ps.get('ID') == pizza_id:
            return {
                'name': ps.get('Status', 'Unknown'),
                'description': ps.get('Description', ''),
                'is_operator': ps.get('IsOperator', False)
            }
    return {'name': 'Unknown', 'description': '', 'is_operator': False}

def get_status_types_for_pizza(pizza_id: str, status_types: List[Dict]) -> List[Dict]:
    """Get all status+division combinations that map to this pizza status."""
    matches = []
    for st in status_types:
        if st.get('PizzaStatusID') == pizza_id:
            # Skip excluded divisions
            division = st.get('DivisionID', '')
            if any(excluded in division for excluded in EXCLUDED_DIVS):
                continue
            
            matches.append({
                'status': st.get('Status'),
                'division': st.get('DivisionID'),
                'order': st.get('OrderID') or '999'
            })
    
    return sorted(matches, key=lambda x: (str(x['order']), str(x['division'])))

def main():
    """Generate pizza status requirements from operator data."""
    base_path = Path(__file__).parent.parent
    
    print("🍕 Generating Pizza Status Requirements from Inference\n")
    print("=" * 70)
    
    # Load data files
    print("\n📂 Loading data files...")
    operators = load_json_data(base_path / 'data' / 'pay_Operators.json')
    certifications = load_json_data(base_path / 'data' / 'pay_Certifications.json')
    status_types = load_json_data(base_path / 'data' / 'pay_StatusTypes.json')
    pizza_statuses = load_json_data(base_path / 'data' / 'pay_PizzaStatuses.json')
    aliases = load_json_data(base_path / 'config' / 'certification_aliases.json')
    
    print(f"   ✓ Operators: {len(operators)}")
    print(f"   ✓ Certifications: {len(certifications)}")
    print(f"   ✓ Status Types: {len(status_types)}")
    print(f"   ✓ Pizza Statuses: {len(pizza_statuses)}")
    
    # Group operators by pizza status
    print("\n🔍 Grouping operators by Pizza Status...")
    pizza_groups = group_operators_by_pizza_status(operators, status_types)
    print(f"   ✓ Found {len(pizza_groups)} unique pizza statuses with operators")
    
    # Analyze each pizza status
    print(f"\n📊 Analyzing certifications (threshold: {REQUIREMENT_THRESHOLD * 100}%)...")
    pizza_requirements = {}
    
    for pizza_id, pizza_operators in pizza_groups.items():
        pizza_info = get_pizza_status_info(pizza_id, pizza_statuses)
        status_mappings = get_status_types_for_pizza(pizza_id, status_types)
        
        print(f"\n   Pizza Status: {pizza_info['name']}")
        print(f"   ID: {pizza_id}")
        print(f"   Operators: {len(pizza_operators)}")
        print(f"   Status+Division mappings: {len(status_mappings)}")
        
        # Infer requirements
        cert_coverage = infer_requirements_for_pizza_status(
            pizza_operators,
            certifications,
            aliases,
            REQUIREMENT_THRESHOLD
        )
        
        required_certs = sorted(cert_coverage.keys())
        print(f"   Required certs (≥{REQUIREMENT_THRESHOLD * 100}%): {len(required_certs)}")
        
        if required_certs:
            for cert_name in required_certs[:5]:  # Show first 5
                info = cert_coverage[cert_name]
                print(f"      • {cert_name}: {info['count']}/{info['total']} ({info['percentage']}%)")
            if len(required_certs) > 5:
                print(f"      ... and {len(required_certs) - 5} more")
        
        # Build pizza status requirement record
        pizza_requirements[pizza_id] = {
            'pizza_status_id': pizza_id,
            'pizza_status_name': pizza_info['name'],
            'description': pizza_info['description'],
            'is_operator': pizza_info['is_operator'],
            'threshold': REQUIREMENT_THRESHOLD,
            'operators_analyzed': len(pizza_operators),
            'required_certifications': [
                {
                    'name': cert_name,
                    'coverage': cert_coverage[cert_name]
                }
                for cert_name in required_certs
            ],
            'status_mappings': status_mappings
        }
    
    # Sort by pizza status name for readability
    sorted_requirements = dict(
        sorted(pizza_requirements.items(), 
               key=lambda x: x[1]['pizza_status_name'])
    )
    
    # Save to file
    output_path = base_path / 'data' / 'pay_PizzaStatusRequirements.json'
    print(f"\n💾 Saving to {output_path.name}...")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sorted_requirements, f, indent=2, ensure_ascii=False)
    
    print(f"   ✓ Saved {len(sorted_requirements)} pizza status requirement definitions")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ Generation Complete!\n")
    print("📄 Output file: data/pay_PizzaStatusRequirements.json")
    print(f"📊 Pizza statuses analyzed: {len(sorted_requirements)}")
    total_required = sum(len(req['required_certifications']) for req in sorted_requirements.values())
    print(f"📋 Total required certifications: {total_required}")
    print(f"🎯 Threshold used: {REQUIREMENT_THRESHOLD * 100}%")
    print("\n💡 This file can now be edited in the HTML editor!")

if __name__ == '__main__':
    main()
