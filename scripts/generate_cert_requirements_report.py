#!/usr/bin/env python3
"""
Generate comprehensive certification requirements report
Based on ACTUAL certification data from operators
"""

import json
import os
from collections import defaultdict, Counter
from datetime import datetime

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'generated', 'generate_artifacts')

def load_json_file(filename):
    """Load a JSON data file"""
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

def _get_cert_name(cert_record):
    """Robustly extract certification name from a record"""
    for key in ['Cert', 'CertName', 'CertificationName', 'Name']:
        val = cert_record.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return None

def _get_operator_id(cert_record):
    """Robustly extract operator id from a cert record"""
    for key in ['OperatorID', 'OperatorId', 'OperatorGuid', 'Operator']: 
        val = cert_record.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return None

def _is_verified(cert_record):
    """Return True if cert is verified (best-effort across possible fields)"""
    truthy = {True, 'true', 'True', 1, '1', 'verified', 'Verified'}
    keys = ['IsVerified', 'Verified', 'Status']
    any_key_present = any(k in cert_record for k in keys)
    for key in keys:
        val = cert_record.get(key)
        if val in truthy:
            return True
    # If no verification indicator present, assume verified
    return not any_key_present

def _is_active(cert_record):
    """Return True if cert is not expired (best-effort across possible fields)"""
    falsy = {True, 'true', 'True', 1, '1'}
    keys = ['IsExpired', 'Expired']
    any_key_present = any(k in cert_record for k in keys)
    for key in keys:
        val = cert_record.get(key)
        if val in falsy:
            return False
    # If no expiration indicator present, assume active
    return True

def get_cert_requirements_by_division_status():
    """Extract actual cert requirements from operator data"""
    certifications = load_json_file('pay_Certifications.txt')
    operators = load_json_file('pay_Operators.txt')
    statuses = load_json_file('pay_StatusTypes.txt')
    
    if not certifications or not operators or not statuses:
        return defaultdict(lambda: defaultdict(Counter)), {}
    
    # Create operator lookup
    operator_map = {op.get('Id') or op.get('ID'): op for op in operators}
    
    # Get status order and CertFlag info
    status_info = {}
    for status in statuses:
        key = (status.get('DivisionID'), status.get('Status'))
        status_info[key] = {
            'OrderID': status.get('OrderID'),
            'CertFlag': status.get('CertFlag', False)
        }
    
    # Map division -> status -> cert requirements (observed)
    division_status_certs = defaultdict(lambda: defaultdict(Counter))
    # Track operator counts per division/status
    operators_by_div_status = defaultdict(set)
    
    for cert in certifications:
        if cert.get('IsDeleted') in [True, 'true', 1]:
            continue
        op_id = _get_operator_id(cert)
        cert_name = _get_cert_name(cert)
        if not cert_name:
            # Fallback: try to infer from type fields
            type_id = cert.get('CertTypeID') or cert.get('CertificationTypeID')
            type_name = cert.get('CertTypeName') or cert.get('CertificationTypeName')
            if isinstance(type_name, str) and type_name.strip():
                cert_name = type_name.strip()
        if not op_id or not cert_name:
            continue
        operator = operator_map.get(op_id)
        if not operator:
            continue
        division = operator.get('DivisionID', 'Unknown')
        status = operator.get('CurrentStatus', 'Unknown')
        # Only count verified and active certs when observing
        if _is_verified(cert) and _is_active(cert):
            division_status_certs[division][status][cert_name] += 1
        # Track operators present at this division/status
        op_key = operator.get('Id') or operator.get('ID')
        if op_key:
            operators_by_div_status[(division, status)].add(op_key)
    
    return division_status_certs, status_info, operators_by_div_status

def identify_common_certs(division_status_certs):
    """Identify the most common certifications across all divisions for ideal list"""
    all_certs = Counter()
    for division, statuses in division_status_certs.items():
        for status, certs in statuses.items():
            all_certs.update(certs)
    return all_certs

def group_related_certs(cert_list):
    """Group related certification names (e.g., variations of Driver's License)"""
    groups = defaultdict(list)
    groupings = {
        'Drivers License': ['driver', 'license', 'dl '],
        'Social Security': ['social security', 'ssn'],
        'Background Check': ['background', 'bgc'],
        'DOT Drug/Alcohol': ['dot drug', 'dot alcohol', 'dot pre-contract', 'dot pre-emp', 'chain of custody', 'ccf', 'donor pass'],
        'NON-DOT Drug/Alcohol': ['non-dot', 'non dot'],
        'Vehicle Registration/Insurance': ['vehicle', 'registration', 'insurance', 'lease'],
        'W9/Tax Forms': ['w9', 'w-9', 'tax'],
        'I-9/E-Verify': ['i-9', 'i9', 'e-verify', 'everify'],
        'Motor Vehicle Report': ['mvr', 'motor vehicle report'],
        'Orientation': ['orientation'],
        'Behind the Wheel': ['behind the wheel', 'btw'],
        'Wheelchair Securement': ['wheelchair', 'wc securement', 'wav'],
        'CTAA': ['ctaa'],
        'Defensive Driving': ['defensive driving'],
        'DOT Physical': ['dot physical', 'physical card'],
        'Workers Comp': ['workers comp', "worker's comp"],
        'Service Agreement': ['service agreement'],
        'Business Formation': ['business formation', 'business license'],
        'Compliance Review': ['compliance review'],
    }
    ungrouped = []
    for cert_name in cert_list:
        cert_lower = cert_name.lower()
        for group_name, keywords in groupings.items():
            if any(keyword in cert_lower for keyword in keywords):
                groups[group_name].append(cert_name)
                break
        else:
            ungrouped.append(cert_name)
    return groups, ungrouped

def generate_report():
    """Generate the complete certification requirements report"""
    print("Generating Certification Requirements Report...")
    division_status_certs, status_info, operators_by_div_status = get_cert_requirements_by_division_status()
    all_certs = identify_common_certs(division_status_certs)
    target_divs = ['2 - IL', '3 - TX', '5 - CA', '6 - FL', '7 - MI', '8 - OH', '10 - OR', '11 - GA', '12 - PA']
    excluded_divs = ['PA - BROOKES', '2 - LAHORE']  # Divisions to exclude from analysis
    report_lines = []
    report_lines.append("=" * 100)
    report_lines.append(" " * 25 + "OPERATOR LIFECYCLE CERTIFICATION REQUIREMENTS")
    report_lines.append(" " * 35 + "Based on Actual Operator Data")
    report_lines.append(" " * 30 + f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 100)
    report_lines.append("")
    # Section 1: Top Certifications (Observed Common)
    report_lines.append("\n" + "=" * 100)
    report_lines.append("SECTION 1: MOST COMMON CERTIFICATIONS (OBSERVED)")
    report_lines.append("=" * 100)
    report_lines.append("")
    report_lines.append("These are the most frequently observed certifications across all operators:")
    report_lines.append("")
    top_certs = all_certs.most_common(50)
    cert_names = [cert_name for cert_name, _ in top_certs]
    groups, ungrouped = group_related_certs(cert_names)
    category_order = [
        'Drivers License', 'Social Security', 'Background Check', 'DOT Drug/Alcohol', 'NON-DOT Drug/Alcohol',
        'Motor Vehicle Report', 'DOT Physical', 'W9/Tax Forms', 'I-9/E-Verify', 'Defensive Driving', 'CTAA',
        'Orientation', 'Behind the Wheel', 'Wheelchair Securement', 'Workers Comp', 'Service Agreement',
        'Business Formation', 'Vehicle Registration/Insurance', 'Compliance Review',
    ]
    for category in category_order:
        if category in groups and groups[category]:
            report_lines.append(f"\n{category}:")
            for cert in groups[category]:
                count = all_certs[cert]
                report_lines.append(f"  • {cert:<65} ({count:>3} operators)")
    if ungrouped:
        report_lines.append(f"\nOther Certifications:")
        for cert in ungrouped:
            count = all_certs[cert]
            report_lines.append(f"  • {cert:<65} ({count:>3} operators)")
    # Section 2: Inferred Required Certifications per Step
    report_lines.append("\n" + "=" * 100)
    report_lines.append("SECTION 2: INFERRED REQUIRED CERTIFICATIONS PER STEP")
    report_lines.append("=" * 100)
    report_lines.append("")
    report_lines.append("For each division/status, we infer required certs by coverage (verified, active).")
    report_lines.append("Default threshold: 70% of operators at that step must hold the cert.")
    report_lines.append("")

    REQUIRED_THRESHOLD = 0.7
    report_lines.append("")
    for div_prefix in target_divs:
        matching_divs = [d for d in division_status_certs.keys() if d.startswith(div_prefix)]
        if matching_divs:
            report_lines.append("\n" + "=" * 100)
            report_lines.append(f"DIVISION: {div_prefix}")
            report_lines.append("=" * 100)
            for div in matching_divs:
                statuses = division_status_certs[div]
                status_list = []
                for status_name in statuses.keys():
                    info = status_info.get((div, status_name), {})
                    order_id = info.get('OrderID')
                    cert_flag = info.get('CertFlag', False)
                    status_list.append((status_name, order_id, cert_flag))
                def sort_key(item):
                    order_id = item[1]
                    if order_id and str(order_id).isdigit():
                        return (0, int(order_id))
                    else:
                        return (1, item[0])
                status_list.sort(key=sort_key)
                for status_name, order_id, cert_flag in status_list:
                    certs = statuses[status_name]
                    total_ops = len(operators_by_div_status.get((div, status_name), set()))
                    required = []
                    if certs and total_ops > 0:
                        for cert_name, count in certs.most_common():
                            coverage = count / total_ops
                            if coverage >= REQUIRED_THRESHOLD:
                                required.append((cert_name, coverage, count))
                    cert_indicator = " [CertGate]" if cert_flag else ""
                    report_lines.append(f"\n  Status: {status_name}{cert_indicator}")
                    if order_id:
                        report_lines.append(f"  Step: {order_id}")
                    report_lines.append(f"  Operators at step: {total_ops}")
                    if required:
                        report_lines.append(f"  Inferred REQUIRED Certifications (>= {int(REQUIRED_THRESHOLD*100)}% coverage):")
                        for cert_name, coverage, count in required:
                            report_lines.append(f"    • {cert_name:<60} {coverage*100:5.1f}% ({count}/{total_ops})")
                    else:
                        report_lines.append("  Inferred REQUIRED Certifications: None met threshold")

    # Section 3: Division-Specific Observed Certifications
    report_lines.append("\n" + "=" * 100)
    report_lines.append("SECTION 3: DIVISION-SPECIFIC OBSERVED CERTIFICATIONS")
    report_lines.append("=" * 100)
    report_lines.append("")
    report_lines.append("Observed verified, active certifications for each status within each division:")
    report_lines.append("")
    for div_prefix in target_divs:
        matching_divs = [d for d in division_status_certs.keys() if d.startswith(div_prefix)]
        if matching_divs:
            report_lines.append("\n" + "=" * 100)
            report_lines.append(f"DIVISION: {div_prefix}")
            report_lines.append("=" * 100)
            for div in matching_divs:
                statuses = division_status_certs[div]
                status_list = []
                for status_name in statuses.keys():
                    info = status_info.get((div, status_name), {})
                    order_id = info.get('OrderID')
                    cert_flag = info.get('CertFlag', False)
                    status_list.append((status_name, order_id, cert_flag))
                def sort_key(item):
                    order_id = item[1]
                    if order_id and str(order_id).isdigit():
                        return (0, int(order_id))
                    else:
                        return (1, item[0])
                status_list.sort(key=sort_key)
                for status_name, order_id, cert_flag in status_list:
                    certs = statuses[status_name]
                    if certs:
                        cert_indicator = " [CertGate]" if cert_flag else ""
                        report_lines.append(f"\n  Status: {status_name}{cert_indicator}")
                        if order_id:
                            report_lines.append(f"  Step: {order_id}")
                        report_lines.append(f"  Certifications (observed):")
                        for cert_name, count in certs.most_common():
                            report_lines.append(f"    • {cert_name:<60} ({count} operators)")
    # Section 4: Summary Statistics
    report_lines.append("\n\n" + "=" * 100)
    report_lines.append("SECTION 4: SUMMARY STATISTICS")
    report_lines.append("=" * 100)
    report_lines.append("")
    total_unique_certs = len(all_certs)
    total_cert_records = sum(all_certs.values())
    report_lines.append(f"Total Unique Certification Types: {total_unique_certs}")
    report_lines.append(f"Total Certification Records: {total_cert_records}")
    report_lines.append("")
    report_lines.append("Division Breakdown:")
    for div_prefix in target_divs:
        matching_divs = [d for d in division_status_certs.keys() if d.startswith(div_prefix)]
        if matching_divs:
            div_cert_count = 0
            for div in matching_divs:
                for status, certs in division_status_certs[div].items():
                    div_cert_count += sum(certs.values())
            report_lines.append(f"  {div_prefix:<20} {div_cert_count:>6} certification records")
    report_lines.append("\n" + "=" * 100)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 100)
    output_path = os.path.join(OUTPUT_DIR, 'Cert_Requirements_Report.txt')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write('\n'.join(report_lines))
    print(f"Report generated: {output_path}")
    print(f"Total unique certifications: {total_unique_certs}")
    print(f"Total certification records analyzed: {total_cert_records}")

if __name__ == '__main__':
    generate_report()

