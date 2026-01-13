#!/usr/bin/env python3
"""
Phase 4: Bottleneck & Process Issue Identification
===================================================
Identifies systemic bottlenecks, process inefficiencies, and structural
issues preventing operators from progressing through the lifecycle.
"""

import json
from collections import defaultdict, Counter
from pathlib import Path

class BottleneckAnalyzer:
    def __init__(self, data_dir='data'):
        self.data_dir = Path(data_dir)
        self.operators = []
        self.status_types = []
        self.cert_types = []
        
        # Define critical thresholds
        self.BOTTLENECK_THRESHOLD = 0.25  # 25% of operators
        self.STAGE_TIME_CONCERN = 30  # days (if we had timestamp data)
        
    def load_data(self):
        """Load necessary data files"""
        print("=" * 80)
        print("PHASE 4: BOTTLENECK & PROCESS ISSUE IDENTIFICATION")
        print("=" * 80)
        print("\n[1/6] Loading data files...")
        
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
        
        # Load cert types
        cert_types_file = self.data_dir / 'pay_CertTypes.txt'
        if cert_types_file.exists():
            with open(cert_types_file, 'r') as f:
                self.cert_types = json.load(f)
            print(f"  ✓ Loaded {len(self.cert_types)} certification requirements")
    
    def identify_volume_bottlenecks(self):
        """Identify stages with abnormally high operator concentrations"""
        print("\n" + "=" * 80)
        print("[2/6] VOLUME BOTTLENECK ANALYSIS")
        print("=" * 80)
        
        # Count operators at each status
        status_counts = Counter()
        order_map = {}
        
        for op in self.operators:
            status = op.get('StatusName') or op.get('CurrentStatus', 'Unknown')
            order = op.get('StatusOrderSequence', '999')
            status_counts[status] += 1
            order_map[status] = int(order) if str(order).isdigit() else 999
        
        total_ops = len(self.operators)
        bottlenecks = []
        
        print(f"\n🔍 Analyzing {total_ops} operators across {len(status_counts)} statuses...")
        print(f"   Bottleneck threshold: {self.BOTTLENECK_THRESHOLD * 100}% of total operators")
        print()
        
        # Identify bottlenecks
        for status, count in status_counts.items():
            percentage = count / total_ops
            if percentage >= self.BOTTLENECK_THRESHOLD:
                severity = "🚨 CRITICAL" if percentage >= 0.5 else "⚠️  WARNING"
                bottlenecks.append({
                    'status': status,
                    'count': count,
                    'percentage': percentage,
                    'order': order_map.get(status, 999),
                    'severity': severity
                })
        
        if bottlenecks:
            print(f"🚨 IDENTIFIED {len(bottlenecks)} VOLUME BOTTLENECKS:\n")
            print(f"{'Status':<45} {'Count':<10} {'% Total':<12} {'Order':<10} {'Severity'}")
            print("-" * 100)
            
            for bn in sorted(bottlenecks, key=lambda x: x['percentage'], reverse=True):
                print(f"{bn['status'][:43]:<45} {bn['count']:<10} {bn['percentage']*100:>6.1f}%     {bn['order']:<10} {bn['severity']}")
            
            # Analyze root causes
            print("\n📊 ROOT CAUSE ANALYSIS:")
            for bn in sorted(bottlenecks, key=lambda x: x['percentage'], reverse=True)[:3]:
                print(f"\n▸ {bn['status']} (Order {bn['order']}):")
                print(f"  • Volume: {bn['count']} operators ({bn['percentage']*100:.1f}%)")
                
                # Check certification requirements
                status_id = next((st.get('Id') for st in self.status_types 
                                if st.get('Status') == bn['status']), None)
                
                if status_id:
                    required_certs = [ct.get('CertificationName') 
                                     for ct in self.cert_types 
                                     if ct.get('StatusTypeID') == status_id and ct.get('Required')]
                    
                    if required_certs:
                        print(f"  • Required Certifications: {len(required_certs)}")
                        for cert in required_certs[:3]:
                            print(f"    - {cert}")
                        if len(required_certs) > 3:
                            print(f"    ... and {len(required_certs) - 3} more")
                    else:
                        print(f"  • No required certifications (may indicate process issue)")
                
                # Potential causes
                print(f"  • Potential Issues:")
                if bn['order'] <= 3:
                    print(f"    - Early-stage bottleneck: Review onboarding process")
                    print(f"    - May indicate recruitment > processing capacity")
                elif bn['order'] in [4, 5, 6, 7]:
                    print(f"    - Mid-stage bottleneck: Review documentation/training processes")
                    print(f"    - Check for certification approval delays")
                elif bn['order'] >= 8:
                    print(f"    - Late-stage bottleneck: Review final approval processes")
                    print(f"    - Check for vehicle/equipment availability issues")
        else:
            print("✓ No severe volume bottlenecks detected")
            print("  (No single status has > 25% of operators)")
    
    def analyze_division_bottlenecks(self):
        """Identify division-specific bottleneck patterns"""
        print("\n" + "=" * 80)
        print("[3/6] DIVISION-SPECIFIC BOTTLENECK ANALYSIS")
        print("=" * 80)
        
        # Group by division and status
        division_status = defaultdict(lambda: Counter())
        
        for op in self.operators:
            division = op.get('DivisionID', 'Unknown')
            status = op.get('StatusName') or op.get('CurrentStatus', 'Unknown')
            division_status[division][status] += 1
        
        print("\n📍 Division-Level Bottlenecks:\n")
        
        division_issues = []
        
        for division in sorted(division_status.keys()):
            statuses = division_status[division]
            total_in_div = sum(statuses.values())
            
            # Find bottlenecks in this division
            div_bottlenecks = []
            for status, count in statuses.items():
                percentage = count / total_in_div if total_in_div > 0 else 0
                if percentage >= 0.4:  # 40% threshold for division-level
                    div_bottlenecks.append({
                        'status': status,
                        'count': count,
                        'percentage': percentage
                    })
            
            if div_bottlenecks:
                print(f"⚠️  {division}:")
                print(f"   Total Operators: {total_in_div}")
                for bn in sorted(div_bottlenecks, key=lambda x: x['percentage'], reverse=True):
                    print(f"   • {bn['status']}: {bn['count']} ops ({bn['percentage']*100:.1f}%)")
                
                division_issues.append(division)
                print()
        
        if not division_issues:
            print("✓ No severe division-specific bottlenecks detected")
        else:
            print(f"\n🚨 {len(division_issues)} divisions with significant bottlenecks")
            print("   These divisions may need targeted intervention or additional resources")
    
    def identify_process_gaps(self):
        """Identify structural gaps in the lifecycle process"""
        print("\n" + "=" * 80)
        print("[4/6] PROCESS GAP IDENTIFICATION")
        print("=" * 80)
        
        # Get unique orders in use
        orders_present = set()
        for op in self.operators:
            order = op.get('StatusOrderSequence')
            if order and str(order).isdigit():
                orders_present.add(int(order))
        
        if not orders_present:
            print("\n⚠️  Cannot analyze process gaps - no order sequence data available")
            return
        
        min_order = min(orders_present)
        max_order = max(orders_present)
        expected_range = set(range(min_order, max_order + 1))
        missing_orders = sorted(expected_range - orders_present)
        
        print(f"\n🔍 Process Coverage Analysis:")
        print(f"   Stage Range: Order {min_order} to {max_order}")
        print(f"   Expected Stages: {len(expected_range)}")
        print(f"   Covered Stages: {len(orders_present)}")
        print(f"   Missing Stages: {len(missing_orders)}")
        
        if missing_orders:
            print(f"\n⚠️  MISSING LIFECYCLE STAGES:")
            print(f"   Orders with NO operators: {missing_orders}")
            print()
            
            for order in missing_orders:
                # Find status name for this order
                status = next((st for st in self.status_types 
                             if st.get('OrderID') == order), None)
                
                if status:
                    status_name = status.get('Status', 'Unknown')
                    division = status.get('DivisionID', 'All')
                    print(f"   Order {order:>2}: {status_name} ({division})")
                    
                    # Determine impact
                    if min_order < order < max_order:
                        print(f"              🚨 CRITICAL: Gap in middle of lifecycle")
                        print(f"              → Operators may be skipping this stage")
                    else:
                        print(f"              ⚠️  Edge stage - may be optional")
                else:
                    print(f"   Order {order:>2}: (Status not found in schema)")
            
            print("\n💡 IMPLICATIONS:")
            print("   • Operators may be progressing without completing required stages")
            print("   • Some stages may be misconfigured or unused")
            print("   • Review lifecycle flow to ensure all required steps are covered")
        else:
            print("\n✓ All stages in expected range have operators")
            print("  Lifecycle appears to be complete with no gaps")
    
    def analyze_certification_bottlenecks(self):
        """Identify bottlenecks caused by certification requirements"""
        print("\n" + "=" * 80)
        print("[5/6] CERTIFICATION-DRIVEN BOTTLENECK ANALYSIS")
        print("=" * 80)
        
        # Group cert requirements by status
        status_cert_counts = defaultdict(int)
        status_required_counts = defaultdict(int)
        
        for cert_type in self.cert_types:
            status_id = cert_type.get('StatusTypeID')
            required = cert_type.get('Required', False)
            
            if status_id:
                status = next((st for st in self.status_types 
                             if st.get('Id') == status_id), None)
                
                if status:
                    status_name = status.get('Status')
                    status_cert_counts[status_name] += 1
                    if required:
                        status_required_counts[status_name] += 1
        
        # Count operators at each status
        operator_counts = Counter()
        for op in self.operators:
            status = op.get('StatusName') or op.get('CurrentStatus', 'Unknown')
            operator_counts[status] += 1
        
        # Identify cert-heavy stages with many operators
        print("\n📋 Certification Load Analysis:\n")
        print(f"{'Status':<40} {'Operators':<12} {'Required':<12} {'Total Certs':<12} {'Risk'}")
        print("-" * 95)
        
        cert_bottlenecks = []
        
        for status in sorted(status_cert_counts.keys()):
            ops_count = operator_counts.get(status, 0)
            required = status_required_counts.get(status, 0)
            total_certs = status_cert_counts.get(status, 0)
            
            # Calculate risk score
            risk_score = (ops_count / 10) * (required / 2)  # Simplified risk calculation
            
            if ops_count > 0 and required >= 3:
                risk_level = "🚨 HIGH" if risk_score > 5 else "⚠️  MEDIUM" if risk_score > 2 else "○ LOW"
                cert_bottlenecks.append({
                    'status': status,
                    'operators': ops_count,
                    'required': required,
                    'total': total_certs,
                    'risk': risk_score
                })
                
                print(f"{status[:38]:<40} {ops_count:<12} {required:<12} {total_certs:<12} {risk_level}")
        
        if cert_bottlenecks:
            print(f"\n💡 CERTIFICATION BOTTLENECK INSIGHTS:")
            high_risk = [cb for cb in cert_bottlenecks if cb['risk'] > 5]
            
            if high_risk:
                print(f"\n🚨 HIGH-RISK STAGES ({len(high_risk)}):")
                for cb in sorted(high_risk, key=lambda x: x['risk'], reverse=True):
                    print(f"   • {cb['status']}")
                    print(f"     - {cb['operators']} operators waiting")
                    print(f"     - {cb['required']} required certifications")
                    print(f"     → Consider: Streamlining cert requirements or increasing processing capacity")
            else:
                print("   ✓ No high-risk certification bottlenecks identified")
        else:
            print("\n⚠️  No certification requirements data available for analysis")
    
    def generate_bottleneck_summary(self):
        """Generate comprehensive bottleneck summary"""
        print("\n" + "=" * 80)
        print("[6/6] BOTTLENECK SUMMARY & PRIORITIZATION")
        print("=" * 80)
        
        # Collect all issues
        issues = []
        
        # Volume issues
        status_counts = Counter()
        for op in self.operators:
            status = op.get('StatusName') or op.get('CurrentStatus', 'Unknown')
            status_counts[status] += 1
        
        total_ops = len(self.operators)
        for status, count in status_counts.items():
            percentage = count / total_ops
            if percentage >= 0.5:
                issues.append(('CRITICAL', f"{count} operators ({percentage*100:.1f}%) stuck at {status}"))
            elif percentage >= 0.25:
                issues.append(('HIGH', f"{count} operators ({percentage*100:.1f}%) at {status}"))
        
        # Present findings
        print(f"\n🎯 PRIORITY ISSUES:")
        
        if issues:
            critical = [i for i in issues if i[0] == 'CRITICAL']
            high = [i for i in issues if i[0] == 'HIGH']
            
            if critical:
                print(f"\n🚨 CRITICAL PRIORITY ({len(critical)}):")
                for _, issue in critical:
                    print(f"   • {issue}")
            
            if high:
                print(f"\n⚠️  HIGH PRIORITY ({len(high)}):")
                for _, issue in high:
                    print(f"   • {issue}")
        else:
            print("\n✓ No critical bottlenecks identified")
            print("  Operator distribution appears healthy")
        
        print("\n" + "=" * 80)
        print("RECOMMENDED IMMEDIATE ACTIONS:")
        print("=" * 80)
        print("1. Address volume bottlenecks (>25% concentration)")
        print("2. Investigate division-specific issues")
        print("3. Review and streamline certification requirements at high-volume stages")
        print("4. Fill process gaps where stages are missing operators")
        print("5. Run phase5_recommendations.py for comprehensive solution plan")
        print("=" * 80)
    
    def run(self):
        """Execute full bottleneck analysis"""
        self.load_data()
        self.identify_volume_bottlenecks()
        self.analyze_division_bottlenecks()
        self.identify_process_gaps()
        self.analyze_certification_bottlenecks()
        self.generate_bottleneck_summary()
        
        print(f"\n✓ Bottleneck analysis complete")

if __name__ == '__main__':
    analyzer = BottleneckAnalyzer()
    analyzer.run()
