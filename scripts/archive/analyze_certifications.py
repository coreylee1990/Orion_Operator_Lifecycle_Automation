#!/usr/bin/env python3
"""
Parse and analyze certification data
Creates a structured report of certifications for operators
"""

import json
from pathlib import Path
from collections import defaultdict

def load_data():
    """Load all data files"""
    data_dir = Path(__file__).parent.parent / 'data'
    
    # Load operators (JSON object with 'operators' key)
    with open(data_dir / 'pay_Operators.txt', 'r') as f:
        operators_data = json.load(f)
        operators = operators_data['operators']
    
    # Load certifications (JSON array)
    with open(data_dir / 'pay_Certifications.txt', 'r') as f:
        certifications = json.load(f)
    
    return operators, certifications

def analyze_certifications(operators, certifications):
    """Analyze certification data"""
    
    # Create operator lookup
    operator_lookup = {op['operatorID']: op for op in operators}
    
    # Group certifications by operator
    certs_by_operator = defaultdict(list)
    for cert in certifications:
        if not cert.get('IsDeleted', False):
            certs_by_operator[cert['OperatorID']].append(cert)
    
    # Certification type statistics
    cert_types = defaultdict(int)
    approved_certs = defaultdict(int)
    rejected_certs = defaultdict(int)
    pending_certs = defaultdict(int)
    
    for cert in certifications:
        if cert.get('IsDeleted'):
            continue
            
        cert_name = cert.get('Cert', 'Unknown')
        cert_types[cert_name] += 1
        
        if cert.get('isApproved'):
            approved_certs[cert_name] += 1
        elif cert.get('IsRejected'):
            rejected_certs[cert_name] += 1
        else:
            pending_certs[cert_name] += 1
    
    # Division statistics
    division_stats = defaultdict(lambda: {'operators': 0, 'total_certs': 0, 'approved': 0, 'pending': 0})
    
    for op_id, certs in certs_by_operator.items():
        if op_id in operator_lookup:
            division = operator_lookup[op_id]['divisionID']
            division_stats[division]['operators'] += 1
            division_stats[division]['total_certs'] += len(certs)
            division_stats[division]['approved'] += sum(1 for c in certs if c.get('isApproved'))
            division_stats[division]['pending'] += sum(1 for c in certs if not c.get('isApproved') and not c.get('IsRejected'))
    
    # Source channel analysis
    channels = defaultdict(int)
    for cert in certifications:
        if cert.get('IsDeleted'):
            continue
        if cert.get('isMobile'):
            channels['Mobile App'] += 1
        elif cert.get('isProviderPortal'):
            channels['Provider Portal'] += 1
        elif cert.get('isOperatorPortal'):
            channels['Operator Portal'] += 1
        elif cert.get('isBackOffice'):
            channels['Back Office'] += 1
        else:
            channels['Unknown'] += 1
    
    return {
        'total_certifications': len([c for c in certifications if not c.get('IsDeleted')]),
        'cert_types': cert_types,
        'approved_certs': approved_certs,
        'rejected_certs': rejected_certs,
        'pending_certs': pending_certs,
        'division_stats': division_stats,
        'channels': channels,
        'operators_with_certs': len(certs_by_operator),
        'total_operators': len(operators)
    }

def generate_report(stats):
    """Generate analysis report"""
    lines = []
    
    lines.append("=" * 80)
    lines.append("CERTIFICATION ANALYSIS REPORT")
    lines.append("=" * 80)
    lines.append("")
    
    lines.append("OVERVIEW")
    lines.append("-" * 80)
    lines.append(f"Total Active Certifications:    {stats['total_certifications']:,}")
    lines.append(f"Total Operators:                {stats['total_operators']:,}")
    lines.append(f"Operators with Certifications:  {stats['operators_with_certs']:,}")
    lines.append(f"Operators without Certs:        {stats['total_operators'] - stats['operators_with_certs']:,}")
    lines.append("")
    
    lines.append("TOP 15 CERTIFICATION TYPES")
    lines.append("-" * 80)
    lines.append(f"{'Certification Type':<50} {'Total':>8} {'Approved':>10} {'Pending':>10}")
    lines.append("-" * 80)
    for cert_name, total in sorted(stats['cert_types'].items(), key=lambda x: x[1], reverse=True)[:15]:
        approved = stats['approved_certs'][cert_name]
        pending = stats['pending_certs'][cert_name]
        lines.append(f"{cert_name[:50]:<50} {total:>8} {approved:>10} {pending:>10}")
    lines.append("")
    
    lines.append("DIVISION STATISTICS")
    lines.append("-" * 80)
    lines.append(f"{'Division':<15} {'Operators':>10} {'Total Certs':>12} {'Approved':>10} {'Pending':>10} {'Avg/Op':>8}")
    lines.append("-" * 80)
    for division, data in sorted(stats['division_stats'].items()):
        avg = data['total_certs'] / data['operators'] if data['operators'] > 0 else 0
        lines.append(f"{division:<15} {data['operators']:>10} {data['total_certs']:>12} "
                    f"{data['approved']:>10} {data['pending']:>10} {avg:>8.1f}")
    lines.append("")
    
    lines.append("SUBMISSION CHANNELS")
    lines.append("-" * 80)
    lines.append(f"{'Channel':<30} {'Count':>10} {'Percentage':>12}")
    lines.append("-" * 80)
    total_channel = sum(stats['channels'].values())
    for channel, count in sorted(stats['channels'].items(), key=lambda x: x[1], reverse=True):
        pct = (count / total_channel * 100) if total_channel > 0 else 0
        lines.append(f"{channel:<30} {count:>10} {pct:>11.1f}%")
    lines.append("")
    
    return "\n".join(lines)

def main():
    """Main execution"""
    print("Loading data...")
    operators, certifications = load_data()
    
    print("Analyzing certifications...")
    stats = analyze_certifications(operators, certifications)
    
    print("Generating report...")
    report = generate_report(stats)
    
    # Save report
    output_dir = Path(__file__).parent.parent / 'generated'
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / 'certification_analysis_report.txt'
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(report)
    print(f"\n✓ Report saved to: {output_file}")

if __name__ == "__main__":
    main()
