#!/usr/bin/env python3
"""
Comprehensive analysis of all certification naming variations across divisions
Identifies which certifications need database standardization
"""

import json
from collections import defaultdict

def normalize_for_grouping(name):
    """Normalize cert name for grouping variations"""
    return name.lower().strip().replace('  ', ' ')

def main():
    print("🔍 COMPREHENSIVE CERTIFICATION NAME VARIATION ANALYSIS")
    print("=" * 120)
    
    # Load data
    with open('../generated/pay_Operators.json', 'r') as f:
        operators = json.load(f)
    
    with open('../generated/cert_requirements_by_status_division.json', 'r') as f:
        requirements = json.load(f)
    
    # Group all cert names by normalized version
    cert_variations = defaultdict(lambda: {
        'names': set(),
        'operator_by_name_div': defaultdict(lambda: defaultdict(int)),
        'requirement_by_name_div': defaultdict(lambda: defaultdict(set))
    })
    
    # Analyze operator certs
    print("\n📊 Analyzing operator certifications...")
    for op in operators:
        div = op.get('DivisionID', '').split(' ')[0] if op.get('DivisionID') else 'Unknown'
        for cert in op.get('certifications', []):
            cert_name = cert.get('CertType', '')
            if cert_name:
                norm = normalize_for_grouping(cert_name)
                cert_variations[norm]['names'].add(cert_name)
                cert_variations[norm]['operator_by_name_div'][cert_name][div] += 1
    
    # Analyze requirement certs
    print("📊 Analyzing certification requirements...")
    for status_name, status_data in requirements.items():
        divisions = status_data.get('divisions', {})
        for div_num, div_data in divisions.items():
            required = div_data.get('required', [])
            for cert_obj in required:
                cert_name = cert_obj.get('cert', '')
                if cert_name:
                    norm = normalize_for_grouping(cert_name)
                    cert_variations[norm]['names'].add(cert_name)
                    cert_variations[norm]['requirement_by_name_div'][cert_name][div_num].add(status_name)
    
    # Find variations (more than one name format)
    variations = {k: v for k, v in cert_variations.items() if len(v['names']) > 1}
    
    print(f"\n✅ Found {len(variations)} certification types with multiple name formats\n")
    print("=" * 120)
    
    variation_summary = []
    
    for norm_name in sorted(variations.keys()):
        data = variations[norm_name]
        names = sorted(data['names'])
        
        print(f"\n{'─' * 120}")
        print(f"CERTIFICATION: {norm_name}")
        print(f"Variations: {len(names)}")
        print(f"{'─' * 120}")
        
        # Analyze each variation
        variation_details = []
        for name in names:
            op_divs = sorted(data['operator_by_name_div'][name].keys())
            req_divs = sorted(data['requirement_by_name_div'][name].keys())
            
            op_count = sum(data['operator_by_name_div'][name].values())
            req_count = len(req_divs)
            
            print(f"\n  '{name}'")
            
            if op_divs:
                div_counts = [f"{div}({data['operator_by_name_div'][name][div]})" for div in op_divs]
                print(f"    Operators: {op_count} total in divisions: {', '.join(div_counts)}")
            
            if req_divs:
                print(f"    Requirements: {req_count} divisions: {', '.join(req_divs)}")
            
            variation_details.append({
                'name': name,
                'operator_count': op_count,
                'operator_divisions': op_divs,
                'requirement_divisions': req_divs,
                'total_usage': op_count + len(req_divs)
            })
        
        # Determine canonical format (most commonly used)
        canonical = max(variation_details, key=lambda x: x['total_usage'])
        
        print(f"\n  ✅ CANONICAL FORMAT: '{canonical['name']}'")
        print(f"     (Used by {canonical['operator_count']} operators + {len(canonical['requirement_divisions'])} requirement divisions)")
        
        # Show what needs to change
        needs_change = [v for v in variation_details if v['name'] != canonical['name']]
        if needs_change:
            print(f"\n  ⚠️  NEEDS STANDARDIZATION:")
            for v in needs_change:
                if v['operator_count'] > 0:
                    print(f"     '{v['name']}' → '{canonical['name']}'")
                    print(f"       {v['operator_count']} operators in divisions: {', '.join(v['operator_divisions'])}")
        
        variation_summary.append({
            'normalized': norm_name,
            'canonical': canonical['name'],
            'variations': [v['name'] for v in variation_details if v['name'] != canonical['name']],
            'operator_changes_needed': sum(v['operator_count'] for v in needs_change),
            'divisions_affected': list(set(sum([v['operator_divisions'] for v in needs_change], [])))
        })
    
    print(f"\n\n{'=' * 120}")
    print("SUMMARY")
    print("=" * 120)
    
    total_changes = sum(v['operator_changes_needed'] for v in variation_summary)
    
    print(f"\nCertification types with variations: {len(variation_summary)}")
    print(f"Total operator records needing update: {total_changes}")
    print(f"\nDivisions affected: {sorted(set(sum([v['divisions_affected'] for v in variation_summary], [])))}")
    
    # Return for use in SQL generation
    return variation_summary, operators

if __name__ == '__main__':
    main()
