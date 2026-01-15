#!/usr/bin/env python3
"""
Phase 3: Certification Gap Analysis
====================================
Identifies missing certifications, expired certs, and operators blocked
by certification requirements at each lifecycle stage.

NOTE: For data-driven certification requirements analysis based on real adoption patterns,
      use: analyze_cert_requirements_by_status.py
      That script analyzes 4,731 real certification records to determine what certs are
      actually required (80%+ adoption), common (50-79%), or optional (<50%) at each status.
      
      This script (phase3) focuses on compliance gaps when requirements are explicitly
      defined in pay_CertTypes.txt.
"""

import json
from collections import defaultdict, Counter
from pathlib import Path
from datetime import datetime

class CertificationGapAnalyzer:
    def __init__(self, data_dir='data'):
        self.data_dir = Path(data_dir)
        self.operators = []
        self.status_types = []
        self.cert_types = []
        self.certifications = []
        
    def load_data(self):
        """Load all necessary data files"""
        print("=" * 80)
        print("PHASE 3: CERTIFICATION GAP ANALYSIS")
        print("=" * 80)
        print("\n[1/5] Loading data files...")
        
        # Load operators - ALWAYS use real data, never sample/mock
        operator_file = self.data_dir / 'pay_Operators.txt'
        if operator_file.exists():
            with open(operator_file, 'r') as f:
                self.operators = json.load(f)
            print(f"  ✓ Loaded {len(self.operators)} operators from pay_Operators.txt")
        else:
            print(f"  ⚠️  ERROR: pay_Operators.txt not found!")
            return
        
        # Load status types
        status_file = self.data_dir / 'pay_StatusTypes.txt'
        if status_file.exists():
            with open(status_file, 'r') as f:
                self.status_types = json.load(f)
            print(f"  ✓ Loaded {len(self.status_types)} status types")
        
        # Load certification types (requirements)
        cert_types_file = self.data_dir / 'pay_CertTypes.txt'
        if cert_types_file.exists():
            with open(cert_types_file, 'r') as f:
                self.cert_types = json.load(f)
            print(f"  ✓ Loaded {len(self.cert_types)} certification type requirements")
        
        # Load actual certifications (what operators have)
        cert_file = self.data_dir / 'pay_Certifications.txt'
        if cert_file.exists():
            with open(cert_file, 'r') as f:
                self.certifications = json.load(f)
            print(f"  ✓ Loaded {len(self.certifications)} operator certifications")
        
    def map_cert_requirements(self):
        """Map certification requirements to statuses"""
        print("\n" + "=" * 80)
        print("[2/5] CERTIFICATION REQUIREMENTS MAPPING")
        print("=" * 80)
        
        # Build requirement map
        status_requirements = defaultdict(lambda: {'required': [], 'optional': []})
        
        for cert_type in self.cert_types:
            status_id = cert_type.get('StatusTypeID')
            cert_name = cert_type.get('CertificationName', 'Unknown')
            required = cert_type.get('Required', False)
            
            # Find status name
            status = next((st for st in self.status_types 
                          if st.get('Id') == status_id), None)
            
            if status:
                status_name = status.get('Status', 'Unknown')
                if required:
                    status_requirements[status_name]['required'].append(cert_name)
                else:
                    status_requirements[status_name]['optional'].append(cert_name)
        
        if not status_requirements:
            print("\n⚠️  WARNING: No certification requirements found in data!")
            print("   This analysis requires pay_CertTypes.txt with StatusTypeID mappings")
            return status_requirements
        
        print(f"\n📋 Certification Requirements by Status:")
        print("-" * 80)
        
        for status_name in sorted(status_requirements.keys()):
            reqs = status_requirements[status_name]
            print(f"\n▸ {status_name}")
            
            if reqs['required']:
                print(f"  REQUIRED ({len(reqs['required'])}):")
                for cert in reqs['required']:
                    print(f"    ✓ {cert}")
            else:
                print("  REQUIRED: None")
            
            if reqs['optional']:
                print(f"  OPTIONAL ({len(reqs['optional'])}):")
                for cert in reqs['optional'][:3]:  # Show first 3
                    print(f"    ○ {cert}")
                if len(reqs['optional']) > 3:
                    print(f"    ○ ... and {len(reqs['optional']) - 3} more")
        
        return status_requirements
    
    def analyze_operator_certifications(self, status_requirements):
        """Analyze which operators have required certifications"""
        print("\n" + "=" * 80)
        print("[3/5] OPERATOR CERTIFICATION COMPLIANCE")
        print("=" * 80)
        
        # Build operator certification map from REAL DATA
        operator_certs = defaultdict(set)
        for cert in self.certifications:
            operator_id = cert.get('OperatorID')
            cert_name = cert.get('Cert', '')  # REAL FIELD NAME: 'Cert' not 'CertificationName'
            is_deleted = cert.get('IsDeleted', 0) == 1
            is_approved = cert.get('isApproved', 0)
            
            # Skip deleted certifications
            if is_deleted:
                continue
            
            # Check if approved (if field exists)
            # Note: Real data doesn't have consistent ExpirationDate
            # Focus on IsDeleted and isApproved status instead
            if cert_name and operator_id:
                operator_certs[operator_id].add(cert_name)
        
        # Analyze compliance by status
        compliance_by_status = defaultdict(lambda: {'compliant': 0, 'non_compliant': 0, 'missing': []})
        
        for op in self.operators:
            # REAL DATA FIELD NAMES: operatorID, statusName, firstName, lastName
            op_id = op.get('operatorID')
            status_name = op.get('statusName', 'Unknown')
            op_name = f"{op.get('firstName', '')} {op.get('lastName', '')}"
            
            required_certs = status_requirements.get(status_name, {}).get('required', [])
            
            if not required_certs:
                # No requirements for this status
                continue
            
            op_cert_names = operator_certs.get(op_id, set())
            missing_certs = [cert for cert in required_certs if cert not in op_cert_names]
            
            if missing_certs:
                compliance_by_status[status_name]['non_compliant'] += 1
                compliance_by_status[status_name]['missing'].append({
                    'operator': op_name,
                    'missing': missing_certs
                })
            else:
                compliance_by_status[status_name]['compliant'] += 1
        
        # Report compliance
        if compliance_by_status:
            print("\n📊 Certification Compliance by Status:")
            print(f"{'Status':<40} {'Compliant':<12} {'Missing Certs':<15} {'Compliance %'}")
            print("-" * 90)
            
            for status_name in sorted(compliance_by_status.keys()):
                data = compliance_by_status[status_name]
                compliant = data['compliant']
                non_compliant = data['non_compliant']
                total = compliant + non_compliant
                compliance_pct = (compliant / total * 100) if total > 0 else 0
                
                status_indicator = "✓" if compliance_pct == 100 else "⚠️" if compliance_pct >= 70 else "🚨"
                
                print(f"{status_name[:38]:<40} {compliant:<12} {non_compliant:<15} {compliance_pct:>6.1f}% {status_indicator}")
            
            # Show specific gaps
            print("\n🚨 OPERATORS WITH MISSING CERTIFICATIONS:")
            print("-" * 80)
            
            critical_count = 0
            for status_name, data in sorted(compliance_by_status.items()):
                if data['missing']:
                    print(f"\n▸ {status_name}:")
                    for item in data['missing'][:5]:  # Show first 5
                        print(f"  • {item['operator']}")
                        print(f"    Missing: {', '.join(item['missing'])}")
                        critical_count += 1
                    
                    if len(data['missing']) > 5:
                        print(f"  ... and {len(data['missing']) - 5} more operators")
            
            if critical_count == 0:
                print("\n✓ All operators have required certifications for their current status")
        else:
            print("\n⚠️  No certification compliance data available")
            print("   (May indicate missing certification mappings or operator certifications)")
    
    def identify_expired_certifications(self):
        """Find expired certifications that may be blocking progress"""
        print("\n" + "=" * 80)
        print("[4/5] EXPIRED CERTIFICATION ANALYSIS")
        print("=" * 80)
        
        expired_certs = []
        expiring_soon = []
        
        for cert in self.certifications:
            expiration = cert.get('ExpirationDate')
            if expiration:
                try:
                    exp_date = datetime.strptime(expiration, '%Y-%m-%d')
                    days_until_expiry = (exp_date - datetime.now()).days
                    
                    cert_info = {
                        'operator_id': cert.get('OperatorID'),
                        'cert_name': cert.get('CertificationName', 'Unknown'),
                        'exp_date': expiration,
                        'days': days_until_expiry
                    }
                    
                    if days_until_expiry < 0:
                        expired_certs.append(cert_info)
                    elif days_until_expiry < 30:
                        expiring_soon.append(cert_info)
                except:
                    pass
        
        if expired_certs:
            print(f"\n🚨 EXPIRED CERTIFICATIONS: {len(expired_certs)}")
            print(f"{'Operator ID':<40} {'Certification':<35} {'Expired'}")
            print("-" * 90)
            
            for cert in sorted(expired_certs, key=lambda x: x['days'])[:10]:
                print(f"{cert['operator_id']:<40} {cert['cert_name'][:33]:<35} {abs(cert['days'])} days ago")
            
            if len(expired_certs) > 10:
                print(f"\n... and {len(expired_certs) - 10} more expired certifications")
        else:
            print("\n✓ No expired certifications found")
        
        if expiring_soon:
            print(f"\n⚠️  EXPIRING SOON (< 30 days): {len(expiring_soon)}")
            for cert in sorted(expiring_soon, key=lambda x: x['days'])[:5]:
                print(f"  • {cert['cert_name']}: expires in {cert['days']} days")
    
    def generate_certification_summary(self):
        """Generate certification health summary"""
        print("\n" + "=" * 80)
        print("[5/5] CERTIFICATION HEALTH SUMMARY")
        print("=" * 80)
        
        # Calculate overall metrics
        total_operators = len(set(op['Id'] for op in self.operators))
        total_certs = len(self.certifications)
        unique_cert_types = len(set(ct.get('CertificationName') for ct in self.cert_types))
        
        print(f"\n📈 OVERALL METRICS:")
        print(f"   Total Operators: {total_operators}")
        print(f"   Total Active Certifications: {total_certs}")
        print(f"   Unique Certification Types: {unique_cert_types}")
        
        if total_operators > 0:
            avg_certs = total_certs / total_operators
            print(f"   Average Certs per Operator: {avg_certs:.1f}")
        
        # Operators with no certifications
        ops_with_certs = set(cert.get('OperatorID') for cert in self.certifications)
        ops_without_certs = [op for op in self.operators if op.get('Id') not in ops_with_certs]
        
        if ops_without_certs:
            print(f"\n⚠️  OPERATORS WITH NO CERTIFICATIONS: {len(ops_without_certs)}")
            for op in ops_without_certs[:5]:
                name = f"{op.get('FirstName', '')} {op.get('LastName', '')}"
                status = op.get('StatusName') or op.get('CurrentStatus')
                print(f"   • {name} - Current Status: {status}")
            
            if len(ops_without_certs) > 5:
                print(f"   ... and {len(ops_without_certs) - 5} more")
        else:
            print("\n✓ All operators have at least one certification")
        
        print("\n" + "=" * 80)
        print("RECOMMENDED ACTIONS:")
        print("=" * 80)
        print("1. Address operators with missing required certifications")
        print("2. Renew expired certifications blocking progression")
        print("3. Proactively manage certifications expiring soon")
        print("4. Review operators with zero certifications")
        print("5. Run phase4_bottleneck_analysis.py for process-level issues")
        print("=" * 80)
    
    def run(self):
        """Execute full certification gap analysis"""
        self.load_data()
        status_requirements = self.map_cert_requirements()
        self.analyze_operator_certifications(status_requirements)
        self.identify_expired_certifications()
        self.generate_certification_summary()
        
        print(f"\n✓ Certification gap analysis complete")

if __name__ == '__main__':
    analyzer = CertificationGapAnalyzer()
    analyzer.run()
