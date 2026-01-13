
import json
import os
import datetime

# --- constants and mocks ---

# Calculate absolute path to data dir assuming this script is in /scripts/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

FILES = {
    'operators': 'pay_Operators.txt',
    'status_types': 'pay_StatusTypes.txt',
    'pizza_statuses': 'pay_PizzaStatuses.txt',
    'certifications': 'pay_Certifications.txt'
}

# Certification Requirements are derived from CertFlag in pay_StatusTypes
# A status with CertFlag=True indicates that certifications must be verified before advancing
# Actual certs are loaded from pay_Certifications data file

# The Master 14-Step Alignment Reference from Instructions.md
# Used as the Source of Truth because pay_StatusTypes.txt contains inconsistent entries (e.g. "BPI" vs "CREDENTIALING")
MASTER_STATUS_MAP = {
    1: "REGISTRATION",
    2: "ONBOARDING",
    3: "CREDENTIALING",
    4: "DOT SCREENING",
    5: "ORIENTATION-BIG STAR SAFETY & SERVICE",
    6: "ORIENTATION-CLIENT HOSTED",
    7: "Approved for CHO (Client Hosted)",
    8: "APPROVED-ORIENTATION BTW",
    9: "COMPLIANCE REVIEW",
    10: "SBPC APPROVED FOR SERVICE",
    11: "Approved for Service",
    12: "APPROVED FOR CONTRACTING",
    13: "APPROVED FOR LEASING",
    14: "IN-SERVICE"
}

# Mock Completed Certifications for specific Operators
# OperatorID -> List of {CertificationTypeID, IsVerified, IsExpired, RecordAt}
# Note: Certification data is now loaded from actual pay_Certifications data file
MOCK_CERTIFICATIONS = {}


class OperatorLifecycleManager:
    def __init__(self):
        self.operators = []
        self.status_types = []
        self.pizza_statuses = []
        self.certifications = []
        self.certifications_by_operator = {}
        self.load_data()

    def load_data(self):
        # Load Operators
        op_path = os.path.join(DATA_DIR, FILES['operators'])
        try:
            with open(op_path, 'r') as f:
                all_ops = json.load(f)
                
            # Filter for specific divisions as requested
            # 2 IL, 3 TX, 5 CA, 6 FL, 7 MI, 8 OH, 10 OR, 11 GA, 12 PA
            target_divisions = ["2 - IL", "3 - TX", "5 - CA", "6 - FL", "7 - MI", "8 - OH", "10 - OR", "11 - GA", "12 - PA"]
            
            self.operators = [
                op for op in all_ops 
                if any(op.get("DivisionID", "").startswith(p) for p in target_divisions)
            ]
            print(f"Loaded {len(self.operators)} operators after filtering for target divisions.")
            
        except Exception as e:
            print(f"Error loading operators: {e}")
            self.operators = []

        # Load Pizza Statuses (Categories)
        ps_path = os.path.join(DATA_DIR, FILES['pizza_statuses'])
        # Store Map of ID -> IsOperator
        self.pizza_is_operator_map = {}
        
        try:
            with open(ps_path, 'r') as f:
                raw_pizza = json.load(f)
                self.pizza_statuses = []
                
                for ps in raw_pizza:
                    pid = ps.get('ID')
                    if not pid: continue
                    
                    is_op = ps.get('IsOperator')
                    # normalize to boolean
                    is_op_bool = (is_op is True or str(is_op).strip() == '1')
                    
                    self.pizza_is_operator_map[pid] = is_op_bool
                    self.pizza_statuses.append(ps)
                    
        except Exception as e:
            print(f"Error loading pizza statuses: {e}")
            self.pizza_statuses = []
            self.pizza_is_operator_map = {}

        # Load Status Types (Granular)
        st_path = os.path.join(DATA_DIR, FILES['status_types'])
        try:
            with open(st_path, 'r') as f:
                raw_statuses = json.load(f)
                self.status_types = []
                
                target_divisions = ["2 - IL", "3 - TX", "5 - CA", "6 - FL", "7 - MI", "8 - OH", "10 - OR", "11 - GA", "12 - PA"]
                
                for st in raw_statuses:
                    # Filter for target divisions
                    if not any(st.get("DivisionID", "").startswith(p) for p in target_divisions):
                        continue
                        
                    # Filter Logic:
                    # Exclude if isDeleted is True
                    if st.get('isDeleted') is True or str(st.get('isDeleted')).lower() == 'true':
                        continue
                        
                    # Exclude if Fleet == True
                    if st.get('Fleet') is True:
                        continue
                        
                    # Exclude if Providers == True
                    if st.get('Providers') is True:
                        continue
                        
                    # REQUIRED: Must be linked to a PizzaStatus with IsOperator=True (or 1)
                    pid = st.get('PizzaStatusID')
                    is_pizza_operator = self.pizza_is_operator_map.get(pid, False)
                    
                    if not is_pizza_operator:
                        continue

                    self.status_types.append(st)
                    
        except Exception as e:
            print(f"Error loading status types: {e}")
            self.status_types = []

        # Load Certifications
        cert_file = os.path.join(DATA_DIR, FILES['certifications'])
        if os.path.exists(cert_file):
            with open(cert_file, 'r') as f:
                self.certifications = json.load(f)
            print(f"✓ Loaded {len(self.certifications)} certifications")
            
            # Build certification lookup by operator
            for cert in self.certifications:
                if not cert.get('IsDeleted', False):
                    op_id = cert.get('OperatorID')
                    if op_id:
                        if op_id not in self.certifications_by_operator:
                            self.certifications_by_operator[op_id] = []
                        self.certifications_by_operator[op_id].append(cert)
        else:
            print(f"⚠ Certifications file not found: {cert_file}")
            self.certifications = []
            self.certifications_by_operator = {}

    def get_operator(self, identifier):
        """Find operator by ID or partial Name"""
        identifier = identifier.lower()
        for op in self.operators:
            f_name = op.get('FirstName', '').lower()
            l_name = op.get('LastName', '').lower()
            op_id = op.get('Id', '').lower()
            
            if identifier in op_id or identifier in f_name or identifier in l_name:
                return op
        return None

    def get_operator_completed_certs(self, operator_id):
        """Get certifications for an operator from actual data"""
        certs = self.certifications_by_operator.get(operator_id, [])
        processed = []
        for c in certs:
            cert_name = c.get('Cert', 'Unknown')
            if cert_name:
                cert_name = cert_name.strip()
            else:
                cert_name = 'Unknown'
            
            processed.append({
                "CertName": cert_name,
                "CertTypeID": c.get('CertTypeID'),
                "IsApproved": c.get('isApproved', False),
                "IsReviewed": c.get('isReviewed', False),
                "Date": c.get('Date'),
                "CompletionDate": c.get('CompletionDate'),
                "ApprovedDate": c.get('ApprovedDate')
            })
        return processed

    def get_current_status_details(self, operator):
        """Get full status object for operator's current status"""
        current_status_name = operator.get('CurrentStatus')
        # This is tricky because pay_Operators has "CurrentStatus" string, 
        # but pay_StatusTypes has "Status" string.
        # We also have StatusOrderSequence.
        
        # Try to match by name first
        for st in self.status_types:
            if st.get('Status') == current_status_name:
                return st
        return None

    def get_next_status_requirements(self, operator):
        """Identify next status and whether it requires certification"""
        current_seq_str = operator.get('StatusOrderSequence', '0')
        try:
            current_seq = int(current_seq_str)
        except:
            current_seq = 0
            
        next_seq = current_seq + 1
        
        # Find the next status
        next_status_name = "Unknown"
        next_requires_cert = False
        
        for st in self.status_types:
            if str(st.get('OrderID')) == str(next_seq):
                next_status_name = st.get('Status')
                next_requires_cert = st.get('CertFlag', False)
                break
        
        # Get operator's current certifications
        op_id = operator.get('Id')
        current_certs = self.get_operator_completed_certs(op_id)
        valid_certs = [c['CertType'] for c in current_certs if c['Status'] == 'Valid']
            
        return {
            "NextSequence": next_seq,
            "NextStatusName": next_status_name,
            "RequiresCertification": next_requires_cert,
            "CurrentValidCerts": valid_certs,
            "CurrentCertifications": current_certs
        }

    def generate_report(self):
        """Report showing which steps require certifications"""
        report = {}
        # Sort status types by OrderID
        def get_order(x):
            oid = x.get('OrderID')
            if oid and isinstance(oid, str) and oid.isdigit():
                return int(oid)
            return 999

        sorted_statuses = sorted(self.status_types, key=get_order)
        
        # Filter unique statuses by OrderID to avoid duplicates
        seen_orders = set()
        
        for st in sorted_statuses:
            order = st.get('OrderID')
            if not order or order in seen_orders:
                continue
            seen_orders.add(order)
            
            status_name = st.get('Status')
            cert_flag = st.get('CertFlag', False)
            cert_text = "Requires Certification" if cert_flag else "No Certification Required"
            
            report[f"Step {order}: {status_name}"] = cert_text
            
        return report


    def get_ordered_flow_data(self):
        """Returns structured data for flowcharts based on MASTER_STATUS_MAP logic"""
        flow_data = []
        
        # Iterate through the defined Master Map 1-14
        for order in sorted(MASTER_STATUS_MAP.keys()):
            status_name = MASTER_STATUS_MAP[order]
            
            # Check if this step generally has CertFlag=True in most divisions
            cert_flag_count = 0
            total_count = 0
            
            for st in self.status_types:
                if str(st.get('OrderID')) == str(order):
                    total_count += 1
                    if st.get('CertFlag') is True:
                        cert_flag_count += 1
            
            # Determine if this step requires certification
            requires_cert = total_count > 0 and (cert_flag_count / total_count) > 0.5
            
            cert_text = "Certification Required" if requires_cert else "No Certification"

            flow_data.append({
                "order": order,
                "name": status_name,
                "requires_certification": requires_cert,
                "cert_requirement_text": cert_text
            })
            
        return flow_data

class ProcessAuditor:
    def __init__(self, status_types):
        self.status_types = status_types
        self.master_map = MASTER_STATUS_MAP
        
    def _normalize_name(self, name):
        """Helper to strict normalize names for comparison"""
        if not name: return ""
        return name.upper().replace(' ', '').replace('-', '').replace('_', '')

    def audit_divisions(self):
        """Analyze gaps per division"""
        divisions = {}
        for st in self.status_types:
            div_id = st.get('DivisionID')
            if not div_id: continue
            if div_id not in divisions:
                divisions[div_id] = []
            divisions[div_id].append(st)
            
        audit_report = []
        
        for div_id, statuses in divisions.items():
            div_report = {"Division": div_id, "MissingSteps": [], "ConfigConflicts": [], "UndefinedCerts": []}
            
            # Map existing order IDs for this division
            div_order_map = {}
            for st in statuses:
                oid = st.get('OrderID')
                if oid and str(oid).isdigit():
                    oid_int = int(oid)
                    if oid_int not in div_order_map:
                        div_order_map[oid_int] = []
                    div_order_map[oid_int].append(st)
            
            # Check 1-14 coverage
            for i in range(1, 15):
                if i not in div_order_map:
                    div_report["MissingSteps"].append(f"Step {i} ({self.master_map.get(i)})")
                else:
                    candidates = div_order_map[i]
                    expected = self.master_map.get(i)
                    
                    # Check if ANY candidate matches the expected name
                    match_found = False
                    for st in candidates:
                        actual = st.get('Status')
                        # Robust comparison: ignore spaces, case, hyphens
                        if self._normalize_name(expected) == self._normalize_name(actual):
                            match_found = True
                            break # Found it, this step is valid logic-wise
                        
                    if not match_found:
                        # Report what we found instead
                        found_names = [f"'{s.get('Status')}' (ID: {s.get('Id')})" for s in candidates]
                        div_report["ConfigConflicts"].append(f"Step {i}: Expected '{expected}', Found: {', '.join(found_names)}")
                    
                    # Check CertFlag vs Known Requirements (Check all candidates)
                    for st in candidates:
                        cert_flag = st.get('CertFlag')
                        actual = st.get('Status')
                        known_reqs = MOCK_REQUIREMENTS.get(str(i), [])
                        
                        if cert_flag is True and not known_reqs:
                             div_report["UndefinedCerts"].append(f"Step {i} ({actual}) has CertFlag=True but no specific certs defined in logic.")
            
            audit_report.append(div_report)
            
        return audit_report

    def generate_division_tables(self):
        """Generates a Markdown table of steps for each division."""
        divisions = {}
        for st in self.status_types:
            div_id = st.get('DivisionID')
            if not div_id: continue
            if div_id not in divisions:
                divisions[div_id] = []
            divisions[div_id].append(st)
            
        report_lines = []
        report_lines.append("# Division Process Steps Tables\n")
        
        # Sort divisions for consistent output
        sorted_divs = sorted(divisions.keys())
        
        for div_id in sorted_divs:
            statuses = divisions[div_id]
            report_lines.append(f"## Division: {div_id}\n")
            report_lines.append("| Order | Status Name | Status ID | CertFlag |")
            report_lines.append("|-------|-------------|-----------|----------|")
            
            # Sort by OrderID
            def get_order(s):
                try:
                    return int(s.get('OrderID', 999))
                except:
                    return 999
            
            # Sort primarily by Order, secondarily by Name
            sorted_statuses = sorted(statuses, key=lambda x: (get_order(x), x.get('Status', '')))
            
            for st in sorted_statuses:
                order = st.get('OrderID', 'N/A')
                name = st.get('Status', 'Unknown')
                sid = st.get('Id', '')
                cflag = st.get('CertFlag', '')
                report_lines.append(f"| {order} | {name} | {sid} | {cflag} |")
            
            report_lines.append("\n")
            
        return "\n".join(report_lines)

    def generate_audit_text(self):
        data = self.audit_divisions()
        lines = ["Orion Process Audit & Gap Analysis", "=================================="]
        
        for item in data:
            if not item['MissingSteps'] and not item['ConfigConflicts'] and not item['UndefinedCerts']:
                continue
                
            lines.append(f"\nDivision: {item['Division']}")
            
            if item['MissingSteps']:
                lines.append("  [CRITICAL] Missing Process Steps:")
                for s in item['MissingSteps']:
                    lines.append(f"    - {s}")
                    
            if item['ConfigConflicts']:
                lines.append("  [WARNING] Naming/Config Conflicts:")
                for c in item['ConfigConflicts']:
                    lines.append(f"    - {c}")

            if item['UndefinedCerts']:
                lines.append("  [GAP] Undefined Certification Requirements (CertFlag is Active):")
                for u in item['UndefinedCerts']:
                    lines.append(f"    - {u}")
                    
        return "\n".join(lines)



# --- Interaction Script ---

def main():
    manager = OperatorLifecycleManager()
    
    print("\n--- Orion Operator Lifecycle Automation ---")
    print(f"Loaded {len(manager.operators)} operators.")
    
    while True:
        print("\nOptions:")
        print("1. Pick an Operator (Search)")
        print("2. View Requirements Report")
        print("q. Quit")
        
        choice = input("Select an option: ")
        
        if choice == '1':
            search = input("Enter Operator Name or ID: ")
            op = manager.get_operator(search)
            if op:
                print(f"\n--- Operator Found: {op.get('FirstName')} {op.get('LastName')} ---")
                print(f"ID: {op.get('Id')}")
                print(f"Current Status: {op.get('CurrentStatus')} (Step {op.get('StatusOrderSequence')})")
                
                # 1. See what they have completed
                print("\n[Completed Certifications]")
                completed = manager.get_operator_completed_certs(op.get('Id'))
                if completed:
                    for c in completed:
                        print(f" - {c['Name']}: {c['Status']}")
                else:
                    print(" - No certifications found (Mock Data)")

                # 2. What they need for next status
                print("\n[Next Status Requirements]")
                next_info = manager.get_next_status_requirements(op)
                print(f"Next Step: {next_info['NextSequence']} ({next_info['NextStatusName']})")
                print(f"Certification Required: {'Yes' if next_info['RequiresCertification'] else 'No'}")
                
                if next_info['CurrentCertifications']:
                    print("\n[Current Certifications]")
                    for c in next_info['CurrentCertifications']:
                        status_icon = "[x]" if c['Status'] == 'Valid' else "[ ]"
                        print(f" {status_icon} {c['CertType']}: {c['Status']}")
                else:
                    print("\n[Current Certifications]")
                    print(" - No certifications found")

            else:
                print("Operator not found.")
                
        elif choice == '2':
            print("\n--- Certification Requirements by Step ---")
            report = manager.generate_report()
            for step, cert_req in report.items():
                print(f"{step}: {cert_req}")
                
        elif choice.lower() == 'q':
            break

if __name__ == "__main__":
    main()
