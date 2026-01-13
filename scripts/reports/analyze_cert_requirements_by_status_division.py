#!/usr/bin/env python3
"""
Analyze certification requirements by status AND division.
Shows what certs are required for each lifecycle status in each division.
"""

import json
from pathlib import Path
from collections import defaultdict

def load_json_data(file_path: Path):
    """Load JSON data from file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data if isinstance(data, list) else data.get('certifications', data.get('operators', []))

def analyze_by_status_division(certifications: list) -> dict:
    """Analyze cert requirements by status and division."""
    
    # Group by status -> division -> operator -> certs
    status_division_data = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
    status_orders = {}
    
    for cert in certifications:
        operator_id = cert.get('ID') or cert.get('OperatorID')
        status_name = cert.get('StatusName', 'Unknown')
        division_id = cert.get('DivisionID', 'Unknown')
        cert_name = cert.get('Cert')
        is_approved = str(cert.get('isApproved', '0')) == '1'
        is_deleted = str(cert.get('IsDeleted', '0')) == '1'
        order_id = cert.get('StatusOrderID', cert.get('OrderID', '99'))
        
        # Track status order
        if status_name not in status_orders:
            status_orders[status_name] = order_id
        
        # Only include approved, non-deleted certifications
        if is_approved and not is_deleted and cert_name:
            status_division_data[status_name][division_id][operator_id].add(cert_name)
    
    # Calculate requirements
    results = {}
    
    for status_name in sorted(status_division_data.keys(), key=lambda s: (status_orders.get(s, '99'), s)):
        results[status_name] = {
            'order': status_orders.get(status_name, '99'),
            'divisions': {}
        }
        
        for division_id in sorted(status_division_data[status_name].keys()):
            operator_certs = status_division_data[status_name][division_id]
            
            # Count cert frequencies
            cert_counts = defaultdict(int)
            for operator_id, certs in operator_certs.items():
                for cert in certs:
                    cert_counts[cert] += 1
            
            total_operators = len(operator_certs)
            
            # Categorize certs by adoption rate
            required = []  # 80%+
            common = []    # 50-79%
            optional = []  # <50%
            
            for cert_name, count in sorted(cert_counts.items(), key=lambda x: (-x[1], x[0])):
                percentage = (count / total_operators) * 100
                cert_info = {
                    'cert': cert_name,
                    'count': count,
                    'total': total_operators,
                    'percentage': round(percentage, 1)
                }
                
                if percentage >= 80:
                    required.append(cert_info)
                elif percentage >= 50:
                    common.append(cert_info)
                else:
                    optional.append(cert_info)
            
            results[status_name]['divisions'][division_id] = {
                'order': status_orders.get(status_name, '99'),
                'total_operators': total_operators,
                'required': required,
                'common': common,
                'optional': optional
            }
    
    return results

def format_report(analysis: dict) -> str:
    """Format analysis as readable text report."""
    
    lines = []
    lines.append("=" * 100)
    lines.append("CERTIFICATION REQUIREMENTS BY STATUS AND DIVISION")
    lines.append("=" * 100)
    lines.append("")
    lines.append("Legend:")
    lines.append("  REQUIRED ✓  = 80%+ of operators have this cert")
    lines.append("  COMMON   •  = 50-79% of operators have this cert")
    lines.append("  OPTIONAL ·  = <50% of operators have this cert")
    lines.append("  NONE     -  = No cert requirements identified (placeholder)")
    lines.append("")
    
    for status_name, status_data in analysis.items():
        order = status_data['order']
        lines.append("")
        lines.append("=" * 100)
        lines.append(f"STATUS: {status_name} (Order: {order})")
        lines.append("=" * 100)
        
        for division_id, div_data in sorted(status_data['divisions'].items()):
            total = div_data['total_operators']
            required = div_data['required']
            common = div_data['common']
            optional = div_data['optional']
            
            lines.append("")
            lines.append(f"  Division: {division_id} ({total} operator{'s' if total != 1 else ''})")
            lines.append("  " + "-" * 96)
            
            if required:
                lines.append("")
                lines.append("  REQUIRED (80%+):")
                for cert in required[:15]:  # Limit to top 15
                    lines.append(f"    ✓ {cert['cert']:<60} {cert['count']}/{cert['total']} ({cert['percentage']}%)")
                if len(required) > 15:
                    lines.append(f"    ... and {len(required) - 15} more")
            
            if common:
                lines.append("")
                lines.append("  COMMON (50-79%):")
                for cert in common[:10]:  # Limit to top 10
                    lines.append(f"    • {cert['cert']:<60} {cert['count']}/{cert['total']} ({cert['percentage']}%)")
                if len(common) > 10:
                    lines.append(f"    ... and {len(common) - 10} more")
            
            if optional and len(optional) <= 5:
                lines.append("")
                lines.append("  OPTIONAL (<50%):")
                for cert in optional[:5]:
                    lines.append(f"    · {cert['cert']:<60} {cert['count']}/{cert['total']} ({cert['percentage']}%)")
            
            if not required and not common:
                lines.append("")
                lines.append("  - No clear certification requirements (placeholder)")
    
    lines.append("")
    lines.append("=" * 100)
    lines.append("END OF REPORT")
    lines.append("=" * 100)
    
    return "\n".join(lines)

def main():
    # Paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_dir = project_root / 'data'
    output_dir = project_root / 'generated'
    output_dir.mkdir(exist_ok=True)
    
    certs_file = data_dir / 'pay_Certifications.json'
    output_txt = output_dir / 'cert_requirements_by_status_division.txt'
    output_json = output_dir / 'cert_requirements_by_status_division.json'
    
    print("=" * 100)
    print("CERTIFICATION REQUIREMENTS BY STATUS AND DIVISION")
    print("=" * 100)
    print(f"Loading certifications from: {certs_file}")
    print()
    
    # Load data
    certifications = load_json_data(certs_file)
    print(f"✓ Loaded {len(certifications)} certification records")
    print()
    
    # Analyze
    print("Analyzing...")
    analysis = analyze_by_status_division(certifications)
    
    # Count stats
    total_statuses = len(analysis)
    total_combinations = sum(len(s['divisions']) for s in analysis.values())
    
    print(f"✓ Analyzed {total_statuses} status types")
    print(f"✓ Found {total_combinations} status-division combinations")
    print()
    
    # Save report
    report = format_report(analysis)
    
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✓ Saved text report: {output_txt}")
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2)
    print(f"✓ Saved JSON data: {output_json}")
    
    print()
    print("=" * 100)
    print("✅ Analysis complete!")
    print("=" * 100)

if __name__ == '__main__':
    main()
