#!/usr/bin/env python3
"""
Analyze certification requirements by operator status using real data.
Examines actual certification patterns to determine what certs are required at each lifecycle stage.
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set

def load_json_data(file_path: Path) -> dict:
    """Load JSON data from file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_cert_requirements_by_status(certifications: List[dict], operators: List[dict]) -> dict:
    """
    Analyze which certifications are commonly held by operators at each status.
    Returns a comprehensive breakdown of cert patterns by status.
    """
    
    # Group certifications by operator and status
    operator_certs_by_status = defaultdict(lambda: defaultdict(set))
    status_details = {}
    
    for cert in certifications:
        operator_id = cert.get('OperatorID')
        status_name = cert.get('StatusName')
        cert_name = cert.get('Cert')
        is_approved = cert.get('isApproved') == '1'
        is_deleted = cert.get('IsDeleted') == '1'
        
        # Only include approved, non-deleted certifications
        if is_approved and not is_deleted and cert_name:
            operator_certs_by_status[status_name][operator_id].add(cert_name)
            
            # Track status details
            if status_name not in status_details:
                status_details[status_name] = {
                    'statusOrderID': cert.get('StatusOrderID', '0'),
                    'divisionID': cert.get('DivisionID', 'Unknown'),
                    'requiresCerts': cert.get('StatusRequiresCerts') == '1'
                }
    
    # Calculate cert frequencies for each status
    results = {}
    
    for status_name, operator_certs in sorted(operator_certs_by_status.items()):
        # Count how many operators at this status have each cert
        cert_counter = Counter()
        for certs in operator_certs.values():
            for cert in certs:
                cert_counter[cert] += 1
        
        total_operators_at_status = len(operator_certs)
        
        # Calculate percentage for each cert
        cert_analysis = []
        for cert_name, count in cert_counter.most_common():
            percentage = (count / total_operators_at_status) * 100
            cert_analysis.append({
                'certName': cert_name,
                'operatorCount': count,
                'totalOperatorsAtStatus': total_operators_at_status,
                'percentage': round(percentage, 1),
                'isCommon': percentage >= 50  # Common if 50%+ have it
            })
        
        results[status_name] = {
            'statusDetails': status_details.get(status_name, {}),
            'totalOperators': total_operators_at_status,
            'certifications': cert_analysis,
            'requiredCerts': [c for c in cert_analysis if c['percentage'] >= 80],  # 80%+ likely required
            'commonCerts': [c for c in cert_analysis if c['isCommon']]
        }
    
    return results

def analyze_cert_progression(certifications: List[dict]) -> dict:
    """
    Analyze which certs are obtained at which status (progression analysis).
    """
    
    # Track first appearance of each cert type for operators
    cert_first_seen = defaultdict(lambda: defaultdict(list))
    
    for cert in certifications:
        operator_id = cert.get('OperatorID')
        status_name = cert.get('StatusName')
        cert_name = cert.get('Cert')
        status_order_str = cert.get('StatusOrderID', '0')
        status_order = int(status_order_str) if status_order_str and status_order_str.strip() else 0
        
        is_approved = cert.get('isApproved') == '1'
        is_deleted = cert.get('IsDeleted') == '1'
        
        if is_approved and not is_deleted and cert_name:
            cert_first_seen[cert_name][status_name].append({
                'operatorID': operator_id,
                'statusOrder': status_order
            })
    
    # Summarize where each cert is typically obtained
    progression = {}
    for cert_name, status_data in sorted(cert_first_seen.items()):
        total_occurrences = sum(len(ops) for ops in status_data.values())
        
        status_breakdown = []
        for status_name, operators in status_data.items():
            status_order = operators[0]['statusOrder'] if operators else 0
            count = len(operators)
            percentage = (count / total_occurrences) * 100
            
            status_breakdown.append({
                'statusName': status_name,
                'statusOrder': status_order,
                'operatorCount': count,
                'percentage': round(percentage, 1)
            })
        
        # Sort by status order
        status_breakdown.sort(key=lambda x: x['statusOrder'])
        
        # Identify primary status (where most operators get this cert)
        primary_status = max(status_breakdown, key=lambda x: x['operatorCount'])
        
        progression[cert_name] = {
            'totalOccurrences': total_occurrences,
            'primaryStatus': primary_status['statusName'],
            'primaryStatusOrder': primary_status['statusOrder'],
            'statusBreakdown': status_breakdown
        }
    
    return progression

def identify_critical_path_certs(cert_by_status: dict, progression: dict) -> List[dict]:
    """
    Identify certifications that appear to be critical for lifecycle progression.
    """
    
    critical_certs = []
    
    for cert_name, prog_data in progression.items():
        # A cert is critical if:
        # 1. It appears in high percentage (80%+) at any status
        # 2. It's obtained early in the lifecycle (statusOrder < 10)
        
        primary_order = prog_data['primaryStatusOrder']
        primary_status = prog_data['primaryStatus']
        
        # Check if this cert has high adoption at its primary status
        status_data = cert_by_status.get(primary_status, {})
        cert_data = next(
            (c for c in status_data.get('certifications', []) if c['certName'] == cert_name),
            None
        )
        
        if cert_data and cert_data['percentage'] >= 80 and primary_order < 15:
            critical_certs.append({
                'certName': cert_name,
                'primaryStatus': primary_status,
                'statusOrder': primary_order,
                'adoptionRate': cert_data['percentage'],
                'totalOccurrences': prog_data['totalOccurrences']
            })
    
    # Sort by status order (when cert is typically obtained)
    critical_certs.sort(key=lambda x: (x['statusOrder'], -x['adoptionRate']))
    
    return critical_certs

def generate_report(cert_by_status: dict, progression: dict, critical_path: List[dict]) -> str:
    """Generate comprehensive text report."""
    
    lines = []
    lines.append("=" * 100)
    lines.append("CERTIFICATION REQUIREMENTS ANALYSIS - REAL DATA")
    lines.append("=" * 100)
    lines.append("")
    
    # Summary
    total_statuses = len(cert_by_status)
    total_unique_certs = len(progression)
    total_critical = len(critical_path)
    
    lines.append("EXECUTIVE SUMMARY")
    lines.append("-" * 100)
    lines.append(f"Total Status Types Analyzed: {total_statuses}")
    lines.append(f"Total Unique Certifications: {total_unique_certs}")
    lines.append(f"Critical Path Certifications: {total_critical}")
    lines.append("")
    
    # Critical path certifications
    lines.append("CRITICAL PATH CERTIFICATIONS (Required for Progression)")
    lines.append("-" * 100)
    lines.append(f"{'Cert Name':<60} {'Status':<30} {'Order':<6} {'Adoption':<10}")
    lines.append("-" * 100)
    
    for cert in critical_path:
        lines.append(
            f"{cert['certName']:<60} "
            f"{cert['primaryStatus']:<30} "
            f"{cert['statusOrder']:<6} "
            f"{cert['adoptionRate']:.1f}%"
        )
    
    lines.append("")
    lines.append("")
    
    # Detailed breakdown by status
    lines.append("CERTIFICATION REQUIREMENTS BY STATUS (Sorted by Lifecycle Order)")
    lines.append("=" * 100)
    
    # Sort statuses by order ID
    def get_order_id(item):
        order_str = item[1]['statusDetails'].get('statusOrderID', '0')
        return int(order_str) if order_str and order_str.strip() else 0
    
    sorted_statuses = sorted(cert_by_status.items(), key=get_order_id)
    
    for status_name, data in sorted_statuses:
        details = data['statusDetails']
        order_id = details.get('statusOrderID', '0')
        requires_certs = details.get('requiresCerts', False)
        
        lines.append("")
        lines.append(f"STATUS: {status_name}")
        lines.append(f"Order: {order_id} | Requires Certs: {'Yes' if requires_certs else 'No'} | Total Operators: {data['totalOperators']}")
        lines.append("-" * 100)
        
        # Show required certs (80%+ adoption)
        required = data['requiredCerts']
        if required:
            lines.append(f"\nREQUIRED Certifications (80%+ adoption):")
            for cert in required:
                lines.append(f"  ✓ {cert['certName']:<65} {cert['operatorCount']}/{cert['totalOperatorsAtStatus']} ({cert['percentage']:.1f}%)")
        
        # Show common certs (50-79% adoption)
        common = [c for c in data['commonCerts'] if c['percentage'] < 80]
        if common:
            lines.append(f"\nCOMMON Certifications (50-79% adoption):")
            for cert in common:
                lines.append(f"  • {cert['certName']:<65} {cert['operatorCount']}/{cert['totalOperatorsAtStatus']} ({cert['percentage']:.1f}%)")
        
        # Show optional certs (<50% adoption)
        optional = [c for c in data['certifications'] if c['percentage'] < 50]
        if optional and len(optional) <= 10:  # Only show if reasonable number
            lines.append(f"\nOPTIONAL Certifications (<50% adoption) [showing up to 10]:")
            for cert in optional[:10]:
                lines.append(f"  · {cert['certName']:<65} {cert['operatorCount']}/{cert['totalOperatorsAtStatus']} ({cert['percentage']:.1f}%)")
        
        lines.append("")
    
    return "\n".join(lines)

def main():
    # Setup paths
    project_root = Path(__file__).parent.parent
    
    operators_file = project_root / 'data' / 'pay_Operators.json'
    certs_file = project_root / 'data' / 'pay_Certifications.json'
    output_file = project_root / 'generated' / 'certification_requirements_analysis.txt'
    output_json = project_root / 'generated' / 'certification_requirements_analysis.json'
    
    print("=" * 100)
    print("CERTIFICATION REQUIREMENTS ANALYSIS")
    print("=" * 100)
    print(f"Loading operators from: {operators_file}")
    print(f"Loading certifications from: {certs_file}")
    print()
    
    # Load data
    operators_data = load_json_data(operators_file)
    certs_data = load_json_data(certs_file)
    
    # Handle both list and dict formats
    operators = operators_data if isinstance(operators_data, list) else operators_data.get('operators', [])
    certifications = certs_data if isinstance(certs_data, list) else certs_data.get('certifications', [])
    
    print(f"✓ Loaded {len(operators)} operators")
    print(f"✓ Loaded {len(certifications)} certification records")
    print()
    print("Analyzing certification patterns by status...")
    
    # Analyze
    cert_by_status = analyze_cert_requirements_by_status(certifications, operators)
    progression = analyze_cert_progression(certifications)
    critical_path = identify_critical_path_certs(cert_by_status, progression)
    
    print(f"✓ Analyzed {len(cert_by_status)} status types")
    print(f"✓ Identified {len(progression)} unique certifications")
    print(f"✓ Found {len(critical_path)} critical path certifications")
    print()
    
    # Generate report
    report = generate_report(cert_by_status, progression, critical_path)
    
    # Save text report
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✓ Saved text report to: {output_file}")
    
    # Save JSON output
    json_output = {
        'summary': {
            'totalStatuses': len(cert_by_status),
            'totalUniqueCertifications': len(progression),
            'totalCriticalPathCerts': len(critical_path)
        },
        'certificationsByStatus': cert_by_status,
        'certificationProgression': progression,
        'criticalPathCertifications': critical_path
    }
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, indent=2)
    
    print(f"✓ Saved JSON analysis to: {output_json}")
    print()
    print("=" * 100)
    print("✅ Analysis complete!")
    print("=" * 100)

if __name__ == '__main__':
    main()
