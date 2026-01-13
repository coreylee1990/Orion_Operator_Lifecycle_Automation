#!/usr/bin/env python3
"""
Generate Compliance Gap Report based on Pizza Status Requirements.

This script uses pay_PizzaStatusRequirements.json which maps pizza statuses
to required certifications. The pizza status grouping provides more consistent
and accurate requirements across divisions.
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set

# Divisions to exclude from analysis
EXCLUDED_DIVS = ['PA - BROOKES', '2 - LAHORE']

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

def get_pizza_status_id(status: str, division: str, status_types: List[Dict]) -> str:
    """Get the PizzaStatusID for a given status and division."""
    for st in status_types:
        if st.get('Status') == status and st.get('DivisionID') == division:
            return st.get('PizzaStatusID', '')
    return ''

def get_required_certs_for_operator(status: str, division: str, status_types: List[Dict], pizza_reqs: Dict) -> Set[str]:
    """
    Get the list of required certifications for an operator based on their
    status and division, using the pizza status requirements.
    """
    # Find the pizza status ID for this status+division combo
    pizza_id = get_pizza_status_id(status, division, status_types)
    
    if not pizza_id or pizza_id not in pizza_reqs:
        return set()
    
    # Get required certs for this pizza status
    pizza_req = pizza_reqs[pizza_id]
    required_certs = set()
    
    for cert_info in pizza_req.get('required_certifications', []):
        cert_name = cert_info.get('name')
        if cert_name:
            required_certs.add(cert_name)
    
    return required_certs

def build_operator_cert_map(certifications, operators: List[Dict]) -> Dict:
    """
    Build a map of operator -> their current certifications.
    Only includes approved, non-deleted certifications.
    Handles both dict (keyed by operator ID) and list formats.
    """
    operator_certs = defaultdict(lambda: {
        'StatusName': None,
        'DivisionID': None,
        'FirstName': None,
        'LastName': None,
        'certs': set()
    })
    
    # If certifications is a dict keyed by operator ID
    if isinstance(certifications, dict):
        for operator in operators:
            operator_id = operator.get('ID') or operator.get('Id')
            division_id = operator.get('DivisionID', 'Unknown')
            status = operator.get('StatusName') or operator.get('CurrentStatus', 'Unknown')
            
            # Skip excluded divisions
            if any(excluded in division_id for excluded in EXCLUDED_DIVS):
                continue
            
            operator_certs[operator_id]['StatusName'] = status
            operator_certs[operator_id]['DivisionID'] = division_id
            operator_certs[operator_id]['FirstName'] = operator.get('FirstName', '')
            operator_certs[operator_id]['LastName'] = operator.get('LastName', '')
            
            # Get certs for this operator
            cert_list = certifications.get(operator_id, [])
            if not isinstance(cert_list, list):
                cert_list = [cert_list]
            
            for cert in cert_list:
                cert_name = cert.get('Cert')
                is_approved = str(cert.get('isApproved', '0')) == '1'
                is_deleted = str(cert.get('IsDeleted', '0')) == '0'
                
                if cert_name and is_approved and is_deleted:
                    operator_certs[operator_id]['certs'].add(cert_name)
    else:
        # Certifications as flat list (old format)
        for cert in certifications:
            operator_id = cert.get('ID') or cert.get('OperatorID')
            division_id = cert.get('DivisionID', 'Unknown')
            cert_name = cert.get('Cert')
            is_approved = str(cert.get('isApproved', '0')) == '1'
            is_deleted = str(cert.get('IsDeleted', '0')) == '1'
            
            # Skip excluded divisions
            if any(excluded in division_id for excluded in EXCLUDED_DIVS):
                continue
            
            if operator_id and cert_name and is_approved and not is_deleted:
                operator_certs[operator_id]['StatusName'] = cert.get('StatusName', 'Unknown')
                operator_certs[operator_id]['DivisionID'] = division_id
                operator_certs[operator_id]['FirstName'] = cert.get('FirstName', '')
                operator_certs[operator_id]['LastName'] = cert.get('LastName', '')
                operator_certs[operator_id]['certs'].add(cert_name)
    
    return operator_certs

def generate_gap_report(operator_certs: Dict, status_types: List[Dict], pizza_reqs: Dict, aliases: Dict) -> Dict:
    """
    Generate compliance gap report showing what certifications each operator is missing.
    Uses pizza status requirements to determine what certs should be held.
    """
    gap_report = {
        'summary': {
            'total_operators': 0,
            'compliant_operators': 0,
            'non_compliant_operators': 0,
            'total_missing_certs': 0
        },
        'by_status': defaultdict(lambda: {
            'total_operators': 0,
            'compliant': 0,
            'non_compliant': 0,
            'missing_cert_counts': defaultdict(int)
        }),
        'by_division': defaultdict(lambda: {
            'total_operators': 0,
            'compliant': 0,
            'non_compliant': 0,
            'missing_cert_counts': defaultdict(int)
        }),
        'operator_gaps': []
    }
    
    for operator_id, op_data in operator_certs.items():
        status = op_data['StatusName']
        division = op_data['DivisionID']
        actual_certs = op_data['certs']
        
        # Normalize actual cert names
        normalized_actual = set()
        for cert in actual_certs:
            normalized_actual.add(normalize_cert_name(cert, aliases))
        
        # Get what they should have (based on pizza status)
        required_certs = get_required_certs_for_operator(status, division, status_types, pizza_reqs)
        
        # Find gaps
        missing_certs = required_certs - normalized_actual
        
        # Update summary
        gap_report['summary']['total_operators'] += 1
        
        if missing_certs:
            gap_report['summary']['non_compliant_operators'] += 1
            gap_report['summary']['total_missing_certs'] += len(missing_certs)
            gap_report['by_status'][status]['non_compliant'] += 1
            gap_report['by_division'][division]['non_compliant'] += 1
            
            for cert in missing_certs:
                gap_report['by_status'][status]['missing_cert_counts'][cert] += 1
                gap_report['by_division'][division]['missing_cert_counts'][cert] += 1
            
            # Record operator-specific gap
            gap_report['operator_gaps'].append({
                'operator_id': operator_id,
                'first_name': op_data['FirstName'],
                'last_name': op_data['LastName'],
                'status': status,
                'division': division,
                'missing_certs': sorted(list(missing_certs)),
                'has_certs': sorted(list(actual_certs)),
                'required_certs': sorted(list(required_certs))
            })
        else:
            gap_report['summary']['compliant_operators'] += 1
            gap_report['by_status'][status]['compliant'] += 1
            gap_report['by_division'][division]['compliant'] += 1
        
        gap_report['by_status'][status]['total_operators'] += 1
        gap_report['by_division'][division]['total_operators'] += 1
    
    return gap_report

def format_text_report(gap_report: Dict) -> str:
    """Format gap report as readable text."""
    lines = []
    
    lines.append("=" * 100)
    lines.append("OPERATOR CERTIFICATION COMPLIANCE GAP REPORT")
    lines.append("Based on Master Requirements Definition")
    lines.append("=" * 100)
    lines.append("")
    
    # Summary
    summary = gap_report['summary']
    lines.append("EXECUTIVE SUMMARY")
    lines.append("-" * 100)
    lines.append(f"Total Operators: {summary['total_operators']}")
    lines.append(f"Compliant: {summary['compliant_operators']} ({summary['compliant_operators']/summary['total_operators']*100:.1f}%)")
    lines.append(f"Non-Compliant: {summary['non_compliant_operators']} ({summary['non_compliant_operators']/summary['total_operators']*100:.1f}%)")
    lines.append(f"Total Missing Certifications: {summary['total_missing_certs']}")
    lines.append("")
    
    # By Status
    lines.append("=" * 100)
    lines.append("COMPLIANCE BY STATUS")
    lines.append("=" * 100)
    lines.append("")
    
    for status, data in sorted(gap_report['by_status'].items()):
        if data['total_operators'] == 0:
            continue
            
        compliance_rate = (data['compliant'] / data['total_operators'] * 100)
        lines.append(f"\n{status}")
        lines.append("-" * 100)
        lines.append(f"Total Operators: {data['total_operators']}")
        lines.append(f"Compliant: {data['compliant']} ({compliance_rate:.1f}%)")
        lines.append(f"Non-Compliant: {data['non_compliant']} ({100-compliance_rate:.1f}%)")
        
        if data['missing_cert_counts']:
            lines.append(f"\nMost Common Missing Certifications:")
            for cert, count in sorted(data['missing_cert_counts'].items(), key=lambda x: -x[1])[:10]:
                lines.append(f"  • {cert}: {count} operators missing")
    
    # By Division
    lines.append("\n" + "=" * 100)
    lines.append("COMPLIANCE BY DIVISION")
    lines.append("=" * 100)
    lines.append("")
    
    for division, data in sorted(gap_report['by_division'].items()):
        if data['total_operators'] == 0:
            continue
            
        compliance_rate = (data['compliant'] / data['total_operators'] * 100)
        lines.append(f"\n{division}")
        lines.append("-" * 100)
        lines.append(f"Total Operators: {data['total_operators']}")
        lines.append(f"Compliant: {data['compliant']} ({compliance_rate:.1f}%)")
        lines.append(f"Non-Compliant: {data['non_compliant']} ({100-compliance_rate:.1f}%)")
        
        if data['missing_cert_counts']:
            lines.append(f"\nMost Common Missing Certifications:")
            for cert, count in sorted(data['missing_cert_counts'].items(), key=lambda x: -x[1])[:10]:
                lines.append(f"  • {cert}: {count} operators missing")
    
    # Operator-Specific Gaps (Top 50)
    lines.append("\n" + "=" * 100)
    lines.append("OPERATOR-SPECIFIC GAPS (Top 50)")
    lines.append("=" * 100)
    lines.append("")
    
    for i, gap in enumerate(gap_report['operator_gaps'][:50], 1):
        lines.append(f"\n{i}. {gap['first_name']} {gap['last_name']} (ID: {gap['operator_id']})")
        lines.append(f"   Status: {gap['status']} | Division: {gap['division']}")
        lines.append(f"   Missing {len(gap['missing_certs'])} certifications:")
        for cert in gap['missing_certs']:
            lines.append(f"      ❌ {cert}")
    
    if len(gap_report['operator_gaps']) > 50:
        lines.append(f"\n... and {len(gap_report['operator_gaps']) - 50} more operators with gaps")
        lines.append("See JSON file for complete list")
    
    lines.append("\n" + "=" * 100)
    lines.append("END OF REPORT")
    lines.append("=" * 100)
    
    return "\n".join(lines)

def main():
    """Main execution."""
    base_path = Path(__file__).parent.parent.parent
    
    print("🍕 Loading pizza status requirements...")
    pizza_reqs = load_json_data(base_path / 'data' / 'pay_PizzaStatusRequirements.json')
    print(f"   ✓ Loaded {len(pizza_reqs)} pizza status definitions")
    
    print("\n📂 Loading operator and certification data...")
    operators = load_json_data(base_path / 'data' / 'pay_Operators.json')
    cert_data = load_json_data(base_path / 'data' / 'pay_Certifications.json')
    status_types = load_json_data(base_path / 'data' / 'pay_StatusTypes.json')
    aliases = load_json_data(base_path / 'config' / 'certification_aliases.json')
    
    print(f"   ✓ Operators: {len(operators)}")
    print(f"   ✓ Status Types: {len(status_types)}")
    
    print("\n🔍 Building operator certification map...")
    operator_certs = build_operator_cert_map(cert_data, operators)
    print(f"   ✓ Found {len(operator_certs)} unique operators with certifications")
    
    print("\n📊 Generating compliance gap report...")
    gap_report = generate_gap_report(operator_certs, status_types, pizza_reqs, aliases)
    
    # Save JSON report
    output_json = base_path / 'generated' / 'compliance_gap_report.json'
    print(f"\nSaving detailed JSON report to: {output_json}")
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(gap_report, f, indent=2, default=list)
    
    # Save text report
    output_txt = base_path / 'generated' / 'compliance_gap_report.txt'
    print(f"Saving summary text report to: {output_txt}")
    text_report = format_text_report(gap_report)
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write(text_report)
    
    # Print summary
    print("\n" + "=" * 80)
    print("COMPLIANCE SUMMARY")
    print("=" * 80)
    summary = gap_report['summary']
    print(f"Total Operators: {summary['total_operators']}")
    print(f"✅ Compliant: {summary['compliant_operators']} ({summary['compliant_operators']/summary['total_operators']*100:.1f}%)")
    print(f"❌ Non-Compliant: {summary['non_compliant_operators']} ({summary['non_compliant_operators']/summary['total_operators']*100:.1f}%)")
    print(f"📋 Total Missing Certs: {summary['total_missing_certs']}")
    print("=" * 80)
    
    print("\n✅ Report generation complete!")
    print(f"   JSON: {output_json}")
    print(f"   Text: {output_txt}")

if __name__ == '__main__':
    main()
