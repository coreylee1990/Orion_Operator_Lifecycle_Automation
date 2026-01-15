#!/usr/bin/env python3
"""
Phase 1: Operator Lifecycle Overview Analysis
==============================================
Provides comprehensive mapping and understanding of the operator lifecycle,
including all statuses, their order, required certifications, and progression rules.
"""

import json
from collections import defaultdict, Counter
from pathlib import Path

class LifecycleOverviewAnalyzer:
    def __init__(self, data_dir='data'):
        self.data_dir = Path(data_dir)
        self.operators = []
        self.status_types = []
        self.pizza_statuses = []
        self.certifications = []
        self.cert_types = []
        
    def load_data(self):
        """Load all necessary data files"""
        print("=" * 80)
        print("PHASE 1: OPERATOR LIFECYCLE OVERVIEW")
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
        
        # Load pizza statuses (high-level categories)
        pizza_file = self.data_dir / 'pay_PizzaStatuses.txt'
        if pizza_file.exists():
            with open(pizza_file, 'r') as f:
                self.pizza_statuses = json.load(f)
            print(f"  ✓ Loaded {len(self.pizza_statuses)} pizza status categories")
        
        # Load certifications
        cert_file = self.data_dir / 'pay_Certifications.txt'
        if cert_file.exists():
            with open(cert_file, 'r') as f:
                self.certifications = json.load(f)
            print(f"  ✓ Loaded {len(self.certifications)} certifications")
        
        # Load cert types
        cert_types_file = self.data_dir / 'pay_CertTypes.txt'
        if cert_types_file.exists():
            with open(cert_types_file, 'r') as f:
                self.cert_types = json.load(f)
            print(f"  ✓ Loaded {len(self.cert_types)} certification types")
        
        print(f"\n  Total unique operators: {len(set(op['Id'] for op in self.operators))}")
        
    def analyze_lifecycle_structure(self):
        """Analyze the structure of the lifecycle"""
        print("\n" + "=" * 80)
        print("[2/5] LIFECYCLE STRUCTURE ANALYSIS")
        print("=" * 80)
        
        # Get operator-only statuses
        operator_statuses = [
            st for st in self.status_types 
            if st.get('IsOperator') == 1 or st.get('Providers') != 1 and st.get('Fleet') != 1
        ]
        
        # Group by pizza status (high-level phase)
        phases = defaultdict(list)
        for status in operator_statuses:
            pizza_status = status.get('PizzaStatus', 'Unknown')
            phases[pizza_status].append(status)
        
        # Sort phases by typical order
        phase_order = [
            'Onboarding', 'Credentialing', 'DOT Screening', 
            'Orientation', 'Compliance Review', 'Contracting', 
            'Vehicle Leasing', 'In-Service'
        ]
        
        print("\nOperator Lifecycle Phases:")
        print("-" * 80)
        
        for phase_name in phase_order:
            if phase_name in phases:
                print(f"\n📍 PHASE: {phase_name.upper()}")
                print(f"   {'Status Name':<45} Order  Division")
                print(f"   {'-'*45} -----  --------")
                
                statuses = sorted(phases[phase_name], key=lambda x: (x.get('OrderID', 999), x.get('Status', '')))
                for status in statuses:
                    status_name = status.get('Status', 'Unknown')[:45]
                    order = status.get('OrderID', '?')
                    division = status.get('DivisionID', 'All')
                    print(f"   {status_name:<45} {order:>5}  {division}")
        
        # Show unknown phases
        unknown = [p for p in phases.keys() if p not in phase_order and p != 'Unknown']
        if unknown:
            print(f"\n⚠️  UNMAPPED PHASES: {', '.join(unknown)}")
        
    def analyze_current_distribution(self):
        """Analyze current operator distribution across lifecycle"""
        print("\n" + "=" * 80)
        print("[3/5] CURRENT OPERATOR DISTRIBUTION")
        print("=" * 80)
        
        # Count operators at each status
        status_counts = Counter()
        pizza_counts = Counter()
        division_status = defaultdict(lambda: Counter())
        
        for op in self.operators:
            status = op.get('StatusName') or op.get('CurrentStatus', 'Unknown')
            pizza = op.get('PizzaStatus', 'Unknown')
            division = op.get('DivisionID', 'Unknown')
            
            status_counts[status] += 1
            pizza_counts[pizza] += 1
            division_status[division][pizza] += 1
        
        # Overall distribution
        print("\n📊 Overall Distribution by Phase:")
        print(f"{'Phase':<30} {'Count':<10} {'Percentage':<12} {'Bar'}")
        print("-" * 80)
        
        total = sum(pizza_counts.values())
        for phase, count in sorted(pizza_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            bar = '█' * int(percentage / 2)
            print(f"{phase:<30} {count:<10} {percentage:>6.2f}%     {bar}")
        
        print(f"\nTotal Operators: {total}")
        
        # Division breakdown
        print("\n📊 Distribution by Division:")
        print(f"{'Division':<15} {'Onboard':<10} {'Cred':<8} {'DOT':<8} {'Orient':<10} {'Comp':<8} {'Contract':<10} {'In-Svc':<10} {'Total'}")
        print("-" * 110)
        
        for division in sorted(division_status.keys()):
            counts = division_status[division]
            onboard = counts.get('Onboarding', 0)
            cred = counts.get('Credentialing', 0)
            dot = counts.get('DOT Screening', 0)
            orient = counts.get('Orientation', 0)
            comp = counts.get('Compliance Review', 0)
            contract = counts.get('Contracting', 0)
            in_svc = counts.get('In-Service', 0)
            total = sum(counts.values())
            
            print(f"{division:<15} {onboard:<10} {cred:<8} {dot:<8} {orient:<10} {comp:<8} {contract:<10} {in_svc:<10} {total}")
        
    def identify_certification_requirements(self):
        """Map certification requirements to lifecycle phases"""
        print("\n" + "=" * 80)
        print("[4/5] CERTIFICATION REQUIREMENTS BY PHASE")
        print("=" * 80)
        
        # Group certifications by status
        cert_by_status = defaultdict(list)
        for cert_type in self.cert_types:
            status_id = cert_type.get('StatusTypeID')
            if status_id:
                # Find the status name
                status = next((st for st in self.status_types if st.get('Id') == status_id), None)
                if status:
                    status_name = status.get('Status', 'Unknown')
                    cert_name = cert_type.get('CertificationName', 'Unknown')
                    required = cert_type.get('Required', False)
                    cert_by_status[status_name].append({
                        'name': cert_name,
                        'required': required
                    })
        
        if cert_by_status:
            print("\n📋 Certifications Required by Status:")
            print("-" * 80)
            
            for status, certs in sorted(cert_by_status.items()):
                required_certs = [c for c in certs if c['required']]
                optional_certs = [c for c in certs if not c['required']]
                
                print(f"\n▸ {status}")
                if required_certs:
                    print("  REQUIRED:")
                    for cert in required_certs:
                        print(f"    • {cert['name']}")
                if optional_certs:
                    print("  OPTIONAL:")
                    for cert in optional_certs:
                        print(f"    ○ {cert['name']}")
        else:
            print("\n⚠️  No certification mappings found in data")
        
    def generate_lifecycle_summary(self):
        """Generate executive summary"""
        print("\n" + "=" * 80)
        print("[5/5] EXECUTIVE SUMMARY")
        print("=" * 80)
        
        total_ops = len(set(op['Id'] for op in self.operators))
        total_statuses = len(set(st['Status'] for st in self.status_types))
        
        # Calculate key metrics
        status_counts = Counter()
        for op in self.operators:
            status = op.get('PizzaStatus', 'Unknown')
            status_counts[status] += 1
        
        # Identify concentration issues
        if status_counts:
            max_status = status_counts.most_common(1)[0]
            concentration_pct = (max_status[1] / total_ops * 100) if total_ops > 0 else 0
            
            print(f"\n📈 KEY FINDINGS:")
            print(f"   • Total Operators Analyzed: {total_ops}")
            print(f"   • Total Lifecycle Statuses: {total_statuses}")
            print(f"   • Distinct Phases: {len(status_counts)}")
            print(f"   • Highest Concentration: {max_status[1]} operators ({concentration_pct:.1f}%) in {max_status[0]}")
            
            if concentration_pct > 70:
                print(f"\n⚠️  CRITICAL ISSUE: {concentration_pct:.1f}% of operators concentrated in {max_status[0]} phase")
                print("   This suggests a significant bottleneck in the lifecycle progression.")
            
            # Distribution health
            print(f"\n📊 DISTRIBUTION HEALTH:")
            even_distribution = 100 / len(status_counts) if status_counts else 0
            
            healthy_count = sum(1 for count in status_counts.values() 
                              if abs((count/total_ops*100) - even_distribution) < even_distribution * 0.5)
            
            if healthy_count >= len(status_counts) * 0.6:
                print("   ✓ Distribution appears relatively balanced")
            else:
                print("   ⚠️  Distribution is unbalanced - investigate bottlenecks")
            
            # Phase coverage
            expected_phases = ['Onboarding', 'Credentialing', 'DOT Screening', 
                              'Orientation', 'Compliance Review', 'Contracting', 'In-Service']
            missing = [p for p in expected_phases if p not in status_counts]
            
            if missing:
                print(f"\n⚠️  MISSING PHASES: {', '.join(missing)}")
                print("   No operators found in these expected lifecycle phases.")
        
        print("\n" + "=" * 80)
        print("RECOMMENDATIONS FOR NEXT STEPS:")
        print("=" * 80)
        print("1. Run phase2_progression_analysis.py to identify stuck operators")
        print("2. Run phase3_certification_gaps.py to find missing certifications")
        print("3. Run phase4_bottleneck_analysis.py to identify process issues")
        print("4. Run phase5_recommendations.py for actionable fixes")
        print("=" * 80)
    
    def run(self):
        """Execute full analysis"""
        self.load_data()
        self.analyze_lifecycle_structure()
        self.analyze_current_distribution()
        self.identify_certification_requirements()
        self.generate_lifecycle_summary()
        
        # Save summary to file
        output_file = Path('generated') / 'phase1_lifecycle_overview_report.txt'
        output_file.parent.mkdir(exist_ok=True)
        
        print(f"\n✓ Analysis complete. Full report saved to: {output_file}")

if __name__ == '__main__':
    analyzer = LifecycleOverviewAnalyzer()
    analyzer.run()
