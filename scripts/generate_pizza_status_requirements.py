#!/usr/bin/env python3
"""
Generate Pizza Status Requirements from Certification Types

This script builds pizza status requirements directly from the pay_CertTypes table.
Each certification type has a PizzaStatusID field that indicates which pizza status
it belongs to. This is the authoritative source for requirements - no inference needed.

The output maps each pizza status to its required certifications.
"""

import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


# Excluded divisions that should not be considered
EXCLUDED_DIVS = ['PA - BROOKES', '2 - LAHORE']


def load_json_data(filepath: Path) -> any:
    """Load JSON data from file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both list and dict formats
    if isinstance(data, dict):
        # If it's a dict, check for common wrapper keys
        if 'certifications' in data:
            return data['certifications']
        elif 'operators' in data:
            return data['operators']
        elif 'statusTypes' in data:
            return data['statusTypes']
        return data
    return data


def get_cert_types_by_pizza_status(cert_types: List[Dict], pizza_statuses: List[Dict], 
                                    aliases: Dict) -> Dict:
    """Group certification types by their PizzaStatusID.
    
    Returns a dict mapping PizzaStatusID to list of required certifications.
    """
    pizza_groups = defaultdict(list)
    
    # Create pizza status lookup for names
    pizza_lookup = {ps['ID']: ps for ps in pizza_statuses}
    
    for cert_type in cert_types:
        pizza_id = cert_type.get('PizzaStatusID')
        
        # Skip if no pizza status or deleted or not required
        if not pizza_id:
            continue
        if cert_type.get('isDeleted', False):
            continue
        if not cert_type.get('isRequired', False):
            continue
            
        # Skip excluded divisions
        division = cert_type.get('DivisionID', '')
        if any(excluded in division for excluded in EXCLUDED_DIVS):
            continue
        
        cert_name = cert_type.get('Certification', '').strip()
        
        # Normalize using aliases - handle both string and list values
        normalized_name = aliases.get(cert_name, cert_name)
        if isinstance(normalized_name, list):
            # If alias maps to a list, use the first (canonical) name
            normalized_name = normalized_name[0] if normalized_name else cert_name
        
        pizza_groups[pizza_id].append({
            'cert_type_id': cert_type.get('ID'),
            'name': normalized_name,
            'original_name': cert_name,
            'division': division,
            'is_required': cert_type.get('isRequired', False),
            'is_deleted': cert_type.get('isDeleted', False)
        })
    
    return dict(pizza_groups)


def deduplicate_cert_names(cert_list: List[Dict]) -> List[Dict]:
    """Remove duplicate certification names, keeping the most common division."""
    # Group by normalized name
    name_groups = defaultdict(list)
    for cert in cert_list:
        # Make sure cert is a dict
        if not isinstance(cert, dict):
            print(f"WARNING: cert is not a dict: {type(cert)} = {cert}")
            continue
        
        cert_name = cert.get('name', '')
        if not cert_name:
            continue
        
        # Make sure name is a string
        if isinstance(cert_name, list):
            print(f"WARNING: cert_name is a list: {cert_name}")
            print(f"Full cert: {cert}")
            continue
            
        name_groups[cert_name].append(cert)
    
    # Keep one per unique name (prefer most common division)
    deduped = []
    for name, certs in name_groups.items():
        # Count divisions
        div_counts = defaultdict(int)
        for cert in certs:
            div_counts[cert['division']] += 1
        
        # Pick the cert with the most common division
        most_common_div = max(div_counts.keys(), key=lambda d: div_counts[d])
        selected = next(c for c in certs if c['division'] == most_common_div)
        deduped.append(selected)
    
    return sorted(deduped, key=lambda c: c['name'])


def get_pizza_status_info(pizza_id: str, pizza_statuses: List[Dict]) -> Dict:
    """Get information about a pizza status."""
    for ps in pizza_statuses:
        if ps.get('ID') == pizza_id:
            return {
                'name': ps.get('Status', ''),
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
    """Generate pizza status requirements from certification types."""
    base_path = Path(__file__).parent.parent
    
    print("🍕 Generating Pizza Status Requirements from Certification Types\n")
    print("=" * 70)
    
    # Load data files
    print("\n📂 Loading data files...")
    cert_types = load_json_data(base_path / 'data' / 'pay_CertTypes.json')
    status_types = load_json_data(base_path / 'data' / 'pay_StatusTypes.json')
    pizza_statuses = load_json_data(base_path / 'data' / 'pay_PizzaStatuses.json')
    aliases = load_json_data(base_path / 'config' / 'certification_aliases.json')
    
    print(f"   ✓ Certification Types: {len(cert_types)}")
    print(f"   ✓ Status Types: {len(status_types)}")
    print(f"   ✓ Pizza Statuses: {len(pizza_statuses)}")
    print(f"   ✓ Aliases: {len(aliases)}")
    
    # Group cert types by pizza status
    print("\n🔍 Grouping certification types by Pizza Status...")
    pizza_cert_groups = get_cert_types_by_pizza_status(cert_types, pizza_statuses, aliases)
    print(f"   ✓ Found {len(pizza_cert_groups)} pizza statuses with cert requirements")
    
    # Build requirements for each pizza status
    print("\n📊 Building requirements...")
    pizza_requirements = {}
    
    for pizza_id, cert_list in sorted(pizza_cert_groups.items()):
        pizza_info = get_pizza_status_info(pizza_id, pizza_statuses)
        status_mappings = get_status_types_for_pizza(pizza_id, status_types)
        
        # Deduplicate cert names (same cert may appear for multiple divisions)
        deduped_certs = deduplicate_cert_names(cert_list)
        
        print(f"\n   Pizza Status: {pizza_info['name']}")
        print(f"   ID: {pizza_id}")
        print(f"   Cert types (all divisions): {len(cert_list)}")
        print(f"   Unique certifications: {len(deduped_certs)}")
        print(f"   Status+Division mappings: {len(status_mappings)}")
        
        if deduped_certs:
            for cert in deduped_certs[:5]:  # Show first 5
                print(f"      • {cert['name']}")
            if len(deduped_certs) > 5:
                print(f"      ... and {len(deduped_certs) - 5} more")
        
        # Build pizza status requirement record
        pizza_requirements[pizza_id] = {
            'pizza_status_id': pizza_id,
            'pizza_status_name': pizza_info['name'],
            'description': pizza_info['description'],
            'is_operator': pizza_info['is_operator'],
            'required_certifications': [
                {
                    'cert_type_id': cert['cert_type_id'],
                    'name': cert['name'],
                    'original_name': cert['original_name'],
                    'division': cert['division']
                }
                for cert in deduped_certs
            ],
            'status_mappings': status_mappings
        }
    
    # Write output
    output_file = base_path / 'data' / 'pay_PizzaStatusRequirements.json'
    print(f"\n💾 Writing output to {output_file.name}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(pizza_requirements, f, indent=2, ensure_ascii=False)
    
    print(f"   ✓ Wrote {len(pizza_requirements)} pizza status requirements")
    
    # Summary
    total_reqs = sum(len(pr['required_certifications']) for pr in pizza_requirements.values())
    print("\n" + "=" * 70)
    print("✅ Generation Complete!")
    print("=" * 70)
    print(f"Pizza Statuses: {len(pizza_requirements)}")
    print(f"Total Requirements: {total_reqs}")
    print(f"Average per status: {total_reqs / len(pizza_requirements):.1f}")
    print(f"Output: {output_file}")
    print("\n💡 Requirements are now based on cert types with PizzaStatusID,")
    print("   not inferred from operator data!")
    print()


if __name__ == '__main__':
    main()
