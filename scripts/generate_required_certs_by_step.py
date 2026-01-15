#!/usr/bin/env python3
"""
Generate a clean, required-only certification report per division/step.
Inference method:
- For each division/status (step), find operators currently at that step.
- Count verified/active certifications they hold.
- A certification is marked as REQUIRED if coverage >= threshold among operators at that step.
Notes:
- Without an explicit DB mapping (e.g., StatusRequirements), this is an empirical inference.
- Threshold is configurable; default 0.8 (80%).
"""

import json
import os
from collections import defaultdict, Counter
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'generated', 'generate_artifacts')

REQUIRED_THRESHOLD = float(os.environ.get('REQUIRED_THRESHOLD', '0.8'))  # 80% default
MIN_STEP_OPS = int(os.environ.get('MIN_STEP_OPS', '3'))                  # Require >=3 ops at step to infer
MIN_CERT_COUNT = int(os.environ.get('MIN_CERT_COUNT', '2'))              # Require at least 2 ops holding cert
TARGET_DIVS = ['2 - IL', '3 - TX', '5 - CA', '6 - FL', '7 - MI', '8 - OH', '10 - OR', '11 - GA', '12 - PA']
EXCLUDED_DIVS = ['PA - BROOKES', '2 - LAHORE']  # Divisions to exclude from all analysis


def load_json_file(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'r') as f:
        return json.load(f)


def get_operator_id(rec):
    for k in ['Id', 'ID']:
        v = rec.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def get_cert_name(rec):
    for k in ['Cert', 'CertName', 'CertificationName', 'Name']:
        v = rec.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    # Fallback to type name fields
    for k in ['CertTypeName', 'CertificationTypeName']:
        v = rec.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def is_deleted(rec):
    return rec.get('IsDeleted') in [True, 'true', 'True', 1, '1']


def is_verified(rec):
    truthy = {True, 'true', 'True', 1, '1', 'verified', 'Verified'}
    keys = ['IsVerified', 'Verified', 'Status']
    any_key_present = any(k in rec for k in keys)
    for key in keys:
        val = rec.get(key)
        if val in truthy:
            return True
    # Assume verified if no indicator
    return not any_key_present


def is_active(rec):
    falsy = {True, 'true', 'True', 1, '1'}
    keys = ['IsExpired', 'Expired']
    for key in keys:
        val = rec.get(key)
        if val in falsy:
            return False
    return True


def build_context():
    certifications = load_json_file('pay_Certifications.txt')
    operators = load_json_file('pay_Operators.txt')
    statuses = load_json_file('pay_StatusTypes.txt')
    pizza_statuses = load_json_file('pay_PizzaStatuses.txt')

    # Operator lookup
    op_map = {get_operator_id(op): op for op in operators}

    # Build pizza IsOperator map
    pizza_is_operator_map = {}
    for ps in pizza_statuses:
        pid = ps.get('ID')
        if not pid:
            continue
        is_op = ps.get('IsOperator')
        is_op_bool = (is_op is True or str(is_op).strip() == '1')
        pizza_is_operator_map[pid] = is_op_bool

    # Filter statuses to match division_process_tables.md logic
    filtered_statuses = []
    for st in statuses:
        div = st.get('DivisionID', '')
        # Skip excluded divisions
        if any(excluded in div for excluded in EXCLUDED_DIVS):
            continue
        if not any(div.startswith(p) for p in TARGET_DIVS):
            continue
        # Exclude deleted
        if st.get('isDeleted') is True or str(st.get('isDeleted')).lower() == 'true':
            continue
        # Exclude Fleet/Providers
        if st.get('Fleet') is True or st.get('Providers') is True:
            continue
        # Must be linked to operator pizza status
        pid = st.get('PizzaStatusID')
        if not pizza_is_operator_map.get(pid, False):
            continue
        filtered_statuses.append(st)

    # Status info per division/status (from filtered set)
    status_info = {}
    for st in filtered_statuses:
        key = (st.get('DivisionID'), st.get('Status'))
        status_info[key] = {
            'OrderID': st.get('OrderID'),
            'CertFlag': st.get('CertFlag', False),
            'StatusID': st.get('Id') or st.get('ID')
        }

    # Operators currently at each division/status
    ops_by_div_status = defaultdict(set)
    for op in operators:
        div = op.get('DivisionID')
        status = op.get('CurrentStatus')
        op_id = get_operator_id(op)
        # Only include statuses that are in filtered_statuses for that division
        if div and status and op_id and (div, status) in status_info:
            ops_by_div_status[(div, status)].add(op_id)

    # Observed cert counts (verified, active) for those operators
    # Observed cert holders (unique operators) for those steps
    observed_certs = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
    for cert in certifications:
        if is_deleted(cert):
            continue
        if not is_verified(cert) or not is_active(cert):
            continue
        op_id = cert.get('OperatorID') or cert.get('OperatorId')
        cert_name = get_cert_name(cert)
        if not op_id or not cert_name:
            continue
        op = op_map.get(op_id)
        if not op:
            continue
        div = op.get('DivisionID')
        status = op.get('CurrentStatus')
        if not div or not status:
            continue
        # Only tally if status/division is in our filtered table
        if (div, status) in status_info:
            # Track unique operator holders per cert
            observed_certs[div][status][cert_name].add(op_id)

    return status_info, ops_by_div_status, observed_certs, filtered_statuses


def infer_required(status_info, ops_by_div_status, observed_certs):
    required_map = defaultdict(lambda: defaultdict(list))
    for (div, status), ops in ops_by_div_status.items():
        if not any(div.startswith(p) for p in TARGET_DIVS):
            continue
        total = len(ops)
        # Only infer if we have sufficient sample size
        if total < MIN_STEP_OPS:
            continue
        certs = observed_certs.get(div, {}).get(status, {})
        for cert_name, holders in certs.items():
            # Unique holders count
            count = len(holders)
            if count < MIN_CERT_COUNT:
                continue
            coverage = count / total
            if coverage >= REQUIRED_THRESHOLD:
                required_map[div][status].append((cert_name, coverage, count, total))
    return required_map


def generate_report():
    status_info, ops_by_div_status, observed_certs, filtered_statuses = build_context()
    required_map = infer_required(status_info, ops_by_div_status, observed_certs)

    lines = []
    lines.append("=" * 100)
    lines.append("REQUIRED CERTIFICATIONS BY STEP (INFERRED)")
    lines.append("".ljust(60) + f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 100)
    lines.append("")
    lines.append(f"Method: A cert is marked REQUIRED if coverage >= {int(REQUIRED_THRESHOLD*100)}% among operators currently at the step.")
    lines.append("Caveat: Without a direct DB mapping, this is an empirical inference.")
    lines.append("")

    # Divisions grouped
    divisions = sorted({div for (div, _) in status_info.keys() if any(div.startswith(p) for p in TARGET_DIVS)}, key=lambda x: int(x.split(' ')[0]))

    for div in divisions:
        lines.append("\n" + "=" * 100)
        lines.append(f"DIVISION: {div}")
        lines.append("=" * 100)
        # statuses in this division (exactly those used in division_process_tables.md), sorted numerically by OrderID
        div_status_rows = [st for st in filtered_statuses if st.get('DivisionID') == div]
        def get_order_int(st):
            oid = st.get('OrderID')
            try:
                return int(oid)
            except Exception:
                return 999
        div_status_rows.sort(key=lambda st: (get_order_int(st), st.get('Status', '')))
        for st in div_status_rows:
            order_id = st.get('OrderID')
            status = st.get('Status')
            cert_flag = st.get('CertFlag', False)
            req = required_map.get(div, {}).get(status, [])
            gate = " [CertGate]" if cert_flag else ""
            lines.append(f"\n  Step: {order_id if order_id is not None else 'N/A'}  Status: {status}{gate}")
            total_ops = len(ops_by_div_status.get((div, status), set()))
            lines.append(f"  Operators at step: {total_ops}")
            if req:
                lines.append(f"  REQUIRED Certifications:")
                for cert_name, coverage, count, total in sorted(req, key=lambda x: (-x[1], x[0])):
                    lines.append(f"    • {cert_name:<60} {coverage*100:5.1f}% ({count}/{total})")
            else:
                if total_ops < MIN_STEP_OPS:
                    lines.append(f"  REQUIRED Certifications: Insufficient sample size (< {MIN_STEP_OPS} ops)")
                else:
                    lines.append("  REQUIRED Certifications: None inferred at threshold")

    out = os.path.join(OUTPUT_DIR, 'Required_Certs_By_Step.txt')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(out, 'w') as f:
        f.write('\n'.join(lines))
    print(f"Report generated: {out}")


if __name__ == '__main__':
    generate_report()
