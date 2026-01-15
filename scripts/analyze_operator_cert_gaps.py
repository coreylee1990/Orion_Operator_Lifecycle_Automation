#!/usr/bin/env python3
"""
Analyze certification GAPS for operator progression.
For each operator, shows what certifications they're MISSING to progress to the next lifecycle status.
"""

import json
from pathlib import Path
from collections import defaultdict

def load_json_data(file_path: Path):
    """Load JSON data from file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data if isinstance(data, list) else data.get('certifications', data.get('operators', []))

def load_pizza_statuses(file_path: Path) -> dict:
    """Load PizzaStatus definitions to filter by IsOperator flag"""
    with open(file_path, 'r', encoding='utf-8') as f:
        pizza_statuses = json.load(f)
    
    # Build map of PizzaStatusID -> IsOperator flag
    pizza_map = {}
    for ps in pizza_statuses:
        pizza_id = ps.get('ID')
        is_operator = ps.get('IsOperator')
        if pizza_id:
            pizza_map[pizza_id] = is_operator is True or str(is_operator).strip() == '1'
    
    return pizza_map

def load_status_types(file_path: Path, pizza_map: dict) -> dict:
    """Load status type definitions from pay_StatusTypes.txt with proper filtering"""
    with open(file_path, 'r', encoding='utf-8') as f:
        status_types = json.load(f)
    
    # Build division -> status -> order mapping
    div_status_order = defaultdict(dict)
    
    for st in status_types:
        # Layer C: Data Hygiene - exclude soft-deleted records
        if str(st.get('isDeleted', False)).lower() == 'true':
            continue
        
        # Layer A: Exclude Non-Operator Actors
        # Rule 1: Exclude Fleet (vehicles)
        fleet = st.get('Fleet')
        if fleet is True or str(fleet).strip() == '1':
            continue
        
        # Rule 2: Exclude Providers (3rd party vendors)
        providers = st.get('Providers')
        if providers is True or str(providers).strip() == '1':
            continue
        
        # Layer B: Structural Integrity - Only include Operator lifecycle statuses
        # Rule 3 & 4: Check PizzaStatus.IsOperator = 1
        pizza_status_id = st.get('PizzaStatusID')
        if not pizza_status_id or not pizza_map.get(pizza_status_id, False):
            continue
            
        div = st.get('DivisionID')
        status = st.get('Status')
        order = st.get('OrderID')
        
        if div and status and order:
            div_status_order[div][status] = order
    
    return div_status_order

def build_status_requirements(certifications: list, status_orders: dict) -> dict:
    """Build a map of what certs are commonly required at each status/division."""
    
    status_div_certs = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    status_div_totals = defaultdict(lambda: defaultdict(int))
    
    for cert in certifications:
        operator_id = cert.get('ID')
        status_name = cert.get('StatusName', 'Unknown')
        division_id = cert.get('DivisionID', 'Unknown')
        cert_name = cert.get('Cert')
        is_approved = str(cert.get('isApproved', '0')) == '1'
        is_deleted = str(cert.get('IsDeleted', '0')) == '1'
        
        if is_approved and not is_deleted and cert_name:
            status_div_certs[status_name][division_id][cert_name] += 1
    
    # Count total operators per status/division
    seen_operators = defaultdict(lambda: defaultdict(set))
    for cert in certifications:
        operator_id = cert.get('ID')
        status_name = cert.get('StatusName', 'Unknown')
        division_id = cert.get('DivisionID', 'Unknown')
        seen_operators[status_name][division_id].add(operator_id)
    
    for status in seen_operators:
        for div in seen_operators[status]:
            status_div_totals[status][div] = len(seen_operators[status][div])
    
    # Calculate required certs (80%+ adoption)
    requirements = {}
    for status_name in status_div_certs:
        requirements[status_name] = {
            'divisions': {}
        }
        
        for division_id in status_div_certs[status_name]:
            total_ops = status_div_totals[status_name][division_id]
            required_certs = []
            
            for cert_name, count in status_div_certs[status_name][division_id].items():
                percentage = (count / total_ops) * 100 if total_ops > 0 else 0
                if percentage >= 80:
                    required_certs.append(cert_name)
            
            requirements[status_name]['divisions'][division_id] = {
                'required_certs': sorted(required_certs),
                'total_operators': total_ops,
                'order': status_orders.get(division_id, {}).get(status_name, '99')
            }
    
    return requirements

def get_operator_certs(operator_id: str, certifications: list) -> set:
    """Get all approved certs for an operator."""
    certs = set()
    for cert in certifications:
        if cert.get('ID') == operator_id:
            is_approved = str(cert.get('isApproved', '0')) == '1'
            is_deleted = str(cert.get('IsDeleted', '0')) == '1'
            cert_name = cert.get('Cert')
            if is_approved and not is_deleted and cert_name:
                certs.add(cert_name)
    return certs

def get_next_status(current_status: str, division_id: str, status_orders: dict) -> tuple:
    """Get the next status in lifecycle progression for this division."""
    try:
        current_order = int(status_orders.get(division_id, {}).get(current_status, '99'))
    except:
        return None, None
    
    # Find next status with higher order in this division
    div_statuses = status_orders.get(division_id, {})
    next_statuses = [(s, int(o)) for s, o in div_statuses.items() if int(o) > current_order]
    if not next_statuses:
        return None, None
    
    next_statuses.sort(key=lambda x: x[1])
    next_status = next_statuses[0][0]
    next_order = next_statuses[0][1]
    return next_status, str(next_order)

def analyze_gaps(operators: list, certifications: list, status_orders: dict) -> list:
    """Analyze certification gaps for each operator."""
    
    requirements = build_status_requirements(certifications, status_orders)
    
    gaps = []
    
    for operator in operators:
        operator_id = operator.get('ID')
        first_name = operator.get('FirstName', '')
        last_name = operator.get('LastName', '')
        email = operator.get('Email', '')
        current_status = operator.get('StatusName', 'Unknown')
        division_id = operator.get('DivisionID', 'Unknown')
        order_id = operator.get('OrderID', '99')
        
        # Get operator's current certs
        current_certs = get_operator_certs(operator_id, certifications)
        
        # Get next status for this division
        next_status, next_order = get_next_status(current_status, division_id, status_orders)
        
        if not next_status:
            # Already at final status or status not found
            gaps.append({
                'operator': {
                    'id': operator_id,
                    'name': f"{first_name} {last_name}".strip(),
                    'email': email,
                    'division': division_id
                },
                'current_status': {
                    'name': current_status,
                    'order': order_id
                },
                'current_certs': sorted(list(current_certs)),
                'next_status': None,
                'required_certs': [],
                'missing_certs': [],
                'has_certs': [],
                'progress': 'FINAL STATUS' if current_status != 'Unknown' else 'UNKNOWN STATUS'
            })
            continue
        
        # Get requirements for next status in this division
        next_reqs = requirements.get(next_status, {}).get('divisions', {}).get(division_id, {})
        required_certs = set(next_reqs.get('required_certs', []))
        
        # Calculate gaps
        missing_certs = sorted(list(required_certs - current_certs))
        has_certs = sorted(list(required_certs & current_certs))
        
        progress_pct = 0
        if required_certs:
            progress_pct = int((len(has_certs) / len(required_certs)) * 100)
        
        gaps.append({
            'operator': {
                'id': operator_id,
                'name': f"{first_name} {last_name}".strip(),
                'email': email,
                'division': division_id
            },
            'current_status': {
                'name': current_status,
                'order': order_id
            },
            'next_status': {
                'name': next_status,
                'order': next_order
            },
            'required_certs': sorted(list(required_certs)),
            'missing_certs': missing_certs,
            'has_certs': has_certs,
            'progress': f"{len(has_certs)}/{len(required_certs)} ({progress_pct}%)" if required_certs else "No requirements"
        })
    
    return gaps

def format_report(gaps: list) -> str:
    """Format gap analysis as text report."""
    
    lines = []
    lines.append("=" * 120)
    lines.append("OPERATOR CERTIFICATION GAP ANALYSIS")
    lines.append("=" * 120)
    lines.append("")
    lines.append("Shows what certifications each operator is MISSING to progress to their next lifecycle status")
    lines.append("")
    
    # Group by current status
    by_status = defaultdict(list)
    for gap in gaps:
        by_status[gap['current_status']['name']].append(gap)
    
    for status_name in sorted(by_status.keys(), key=lambda s: (by_status[s][0]['current_status']['order'], s)):
        operators = by_status[status_name]
        
        lines.append("")
        lines.append("=" * 120)
        lines.append(f"CURRENT STATUS: {status_name} ({len(operators)} operator{'s' if len(operators) != 1 else ''})")
        lines.append("=" * 120)
        
        for gap in sorted(operators, key=lambda x: x['operator']['name']):
            lines.append("")
            lines.append(f"Operator: {gap['operator']['name']} ({gap['operator']['division']})")
            lines.append(f"Email: {gap['operator']['email']}")
            lines.append(f"Current Status: {gap['current_status']['name']} (Order: {gap['current_status']['order']})")
            
            if gap['next_status']:
                lines.append(f"Next Status: {gap['next_status']['name']} (Order: {gap['next_status']['order']})")
                lines.append(f"Progress: {gap['progress']}")
                lines.append("")
                
                if gap['missing_certs']:
                    lines.append(f"❌ MISSING CERTS ({len(gap['missing_certs'])}):")
                    for cert in gap['missing_certs']:
                        lines.append(f"  - {cert}")
                else:
                    lines.append("✅ All required certs obtained for next status!")
                
                if gap['has_certs']:
                    lines.append("")
                    lines.append(f"✓ Already has ({len(gap['has_certs'])}):")
                    for cert in gap['has_certs'][:5]:
                        lines.append(f"  + {cert}")
                    if len(gap['has_certs']) > 5:
                        lines.append(f"  + ... and {len(gap['has_certs']) - 5} more")
            else:
                lines.append(f"Status: {gap['progress']}")
            
            lines.append("-" * 120)
    
    lines.append("")
    lines.append("=" * 120)
    lines.append("END OF REPORT")
    lines.append("=" * 120)
    
    return "\n".join(lines)

def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_dir = project_root / 'data'
    output_dir = project_root / 'generated'
    output_dir.mkdir(exist_ok=True)
    
    operators_file = data_dir / 'pay_Operators.json'
    certs_file = data_dir / 'pay_Certifications.json'
    status_types_file = data_dir / 'pay_StatusTypes.txt'
    pizza_statuses_file = data_dir / 'pay_PizzaStatuses.txt'
    output_txt = output_dir / 'operator_certification_gaps.txt'
    output_json = output_dir / 'operator_certification_gaps.json'
    
    print("=" * 120)
    print("OPERATOR CERTIFICATION GAP ANALYSIS")
    print("=" * 120)
    print(f"Loading operators from: {operators_file}")
    print(f"Loading certifications from: {certs_file}")
    print(f"Loading status types from: {status_types_file}")
    print(f"Loading pizza statuses from: {pizza_statuses_file}")
    print()
    
    operators = load_json_data(operators_file)
    certifications = load_json_data(certs_file)
    pizza_map = load_pizza_statuses(pizza_statuses_file)
    status_orders = load_status_types(status_types_file, pizza_map)
    
    print(f"✓ Loaded {len(operators)} operators")
    print(f"✓ Loaded {len(certifications)} certification records")
    print(f"✓ Loaded {len(pizza_map)} pizza status definitions")
    print(f"✓ Loaded status progressions for {len(status_orders)} divisions (filtered by IsOperator=1, Fleet=0, Providers=0)")
    print()
    
    print("Analyzing certification gaps...")
    gaps = analyze_gaps(operators, certifications, status_orders)
    
    # Stats
    total_with_gaps = sum(1 for g in gaps if g.get('missing_certs'))
    total_ready = sum(1 for g in gaps if not g.get('missing_certs') and g.get('next_status'))
    
    print(f"✓ Analyzed {len(gaps)} operators")
    print(f"  - {total_with_gaps} operators have missing certifications")
    print(f"  - {total_ready} operators are ready to progress")
    print()
    
    # Save
    report = format_report(gaps)
    
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✓ Saved text report: {output_txt}")
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(gaps, f, indent=2)
    print(f"✓ Saved JSON data: {output_json}")
    
    print()
    print("=" * 120)
    print("✅ Gap analysis complete!")
    print("=" * 120)

if __name__ == '__main__':
    main()
