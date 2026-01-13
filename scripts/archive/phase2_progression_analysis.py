#!/usr/bin/env python3
"""
Phase 2: Status Progression & Velocity Analysis
================================================
Identifies operators stuck at specific stages, measures progression velocity,
and highlights abnormal patterns in the lifecycle flow.
"""

import json
from collections import defaultdict, Counter
from pathlib import Path
from datetime import datetime, timedelta

class ProgressionAnalyzer:
    def __init__(self, data_dir='data'):
        self.data_dir = Path(data_dir)
        self.operators = []
        self.status_types = []
        
        # Expected progression order (by OrderID)
        self.expected_flow = [
            'REGISTRATION',
            'ONBOARDING',
            'CREDENTIALING',
            'DOT SCREENING',
            'ORIENTATION-BIG STAR SAFETY & SERVICE',
            'APPROVED-ORIENTATION BTW',
            'APPROVED FOR CHO (CLIENT HOSTED)',
            'COMPLIANCE REVIEW',
            'SBPC APPROVED FOR SERVICE',
            'APPROVED FOR CONTRACTING',
            'APPROVED FOR LEASING',
            'IN-SERVICE'
        ]
        
    def load_data(self):
        """Load necessary data files"""
        print("=" * 80)
        print("PHASE 2: STATUS PROGRESSION & VELOCITY ANALYSIS")
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
        
        # Load status types for order sequence
        status_file = self.data_dir / 'pay_StatusTypes.txt'
        if status_file.exists():
            with open(status_file, 'r') as f:
                self.status_types = json.load(f)
            print(f"  ✓ Loaded {len(self.status_types)} status types")
        
        print(f"  Total operators to analyze: {len(self.operators)}")
        
    def analyze_status_distribution(self):
        """Analyze where operators are currently stuck"""
        print("\n" + "=" * 80)
        print("[2/6] CURRENT STATUS DISTRIBUTION")
        print("=" * 80)
        
        # Group operators by status
        status_operators = defaultdict(list)
        order_map = {}
        
        for op in self.operators:
            status_name = op.get('StatusName') or op.get('CurrentStatus', 'Unknown')
            order = op.get('StatusOrderSequence', '999')
            
            status_operators[status_name].append(op)
            order_map[status_name] = int(order) if str(order).isdigit() else 999
        
        # Sort by order sequence
        sorted_statuses = sorted(status_operators.items(), 
                                key=lambda x: (order_map.get(x[0], 999), x[0]))
        
        print("\n📊 Operators by Status (sorted by lifecycle order):")
        print(f"{'Order':<8} {'Status':<45} {'Count':<10} {'% of Total':<12} {'Bar'}")
        print("-" * 100)
        
        total = len(self.operators)
        for status_name, ops_list in sorted_statuses:
            count = len(ops_list)
            percentage = (count / total * 100) if total > 0 else 0
            order = order_map.get(status_name, 999)
            bar = '█' * int(percentage / 2)
            
            print(f"{order:<8} {status_name[:43]:<45} {count:<10} {percentage:>6.2f}%     {bar}")
        
        # Identify bottlenecks (>15% of operators)
        print("\n🚨 POTENTIAL BOTTLENECKS (>15% of operators):")
        bottlenecks = [(status, len(ops)) for status, ops in status_operators.items() 
                       if len(ops) / total > 0.15]
        
        if bottlenecks:
            for status, count in sorted(bottlenecks, key=lambda x: x[1], reverse=True):
                pct = count / total * 100
                print(f"   • {status}: {count} operators ({pct:.1f}%)")
                print(f"     Order: {order_map.get(status, 'Unknown')}")
        else:
            print("   ✓ No severe bottlenecks detected")
        
    def analyze_division_progression(self):
        """Analyze progression patterns by division"""
        print("\n" + "=" * 80)
        print("[3/6] DIVISION-LEVEL PROGRESSION ANALYSIS")
        print("=" * 80)
        
        # Group by division and status
        division_data = defaultdict(lambda: defaultdict(list))
        
        for op in self.operators:
            division = op.get('DivisionID', 'Unknown')
            status_name = op.get('StatusName') or op.get('CurrentStatus', 'Unknown')
            order = int(op.get('StatusOrderSequence', '999'))
            
            division_data[division][order].append({
                'status': status_name,
                'operator': f"{op.get('FirstName', '')} {op.get('LastName', '')}"
            })
        
        print("\n📍 Division Performance Summary:")
        print(f"{'Division':<15} {'Avg Stage':<12} {'Earliest':<10} {'Latest':<10} {'Spread':<10} {'Total Ops'}")
        print("-" * 80)
        
        for division in sorted(division_data.keys()):
            orders = []
            for order, ops_list in division_data[division].items():
                orders.extend([order] * len(ops_list))
            
            if orders:
                avg_stage = sum(orders) / len(orders)
                earliest = min(orders)
                latest = max(orders)
                spread = latest - earliest
                total_ops = len(orders)
                
                # Health indicator
                health = "✓" if spread <= 5 else "⚠️" if spread <= 10 else "🚨"
                
                print(f"{division:<15} {avg_stage:<12.1f} {earliest:<10} {latest:<10} {spread:<10} {total_ops} {health}")
        
        print("\nHealth Indicators:")
        print("  ✓  = Healthy (spread ≤ 5 stages)")
        print("  ⚠️  = Concerning (spread 6-10 stages)")
        print("  🚨 = Critical (spread > 10 stages)")
        
    def identify_stuck_operators(self):
        """Identify operators at early stages (potential issues)"""
        print("\n" + "=" * 80)
        print("[4/6] STUCK OPERATORS ANALYSIS")
        print("=" * 80)
        
        # Operators in early stages (order < 5)
        early_stage_ops = []
        for op in self.operators:
            order = int(op.get('StatusOrderSequence', '999'))
            if order < 5:
                early_stage_ops.append({
                    'id': op.get('Id'),
                    'name': f"{op.get('FirstName', '')} {op.get('LastName', '')}",
                    'division': op.get('DivisionID', 'Unknown'),
                    'status': op.get('StatusName') or op.get('CurrentStatus'),
                    'order': order
                })
        
        if early_stage_ops:
            print(f"\n⚠️  Found {len(early_stage_ops)} operators in early stages (Order < 5):")
            print(f"{'Name':<30} {'Division':<15} {'Status':<35} {'Order'}")
            print("-" * 90)
            
            for op in sorted(early_stage_ops, key=lambda x: x['order']):
                print(f"{op['name'][:28]:<30} {op['division']:<15} {op['status'][:33]:<35} {op['order']}")
            
            print(f"\n💡 These operators may need attention to progress through the lifecycle.")
        else:
            print("\n✓ No operators stuck in very early stages")
        
    def analyze_progression_gaps(self):
        """Identify unusual progression patterns (skipped stages)"""
        print("\n" + "=" * 80)
        print("[5/6] PROGRESSION GAP ANALYSIS")
        print("=" * 80)
        
        # Get all unique order sequences present
        present_orders = set()
        for op in self.operators:
            order = op.get('StatusOrderSequence')
            if order and str(order).isdigit():
                present_orders.add(int(order))
        
        if present_orders:
            min_order = min(present_orders)
            max_order = max(present_orders)
            expected_range = set(range(min_order, max_order + 1))
            missing_orders = expected_range - present_orders
            
            print(f"\n📊 Lifecycle Coverage:")
            print(f"   Minimum Stage Order: {min_order}")
            print(f"   Maximum Stage Order: {max_order}")
            print(f"   Total Range: {len(expected_range)} stages")
            print(f"   Covered Stages: {len(present_orders)} stages")
            print(f"   Missing Stages: {len(missing_orders)} stages")
            
            if missing_orders:
                print(f"\n⚠️  MISSING STAGE ORDERS: {sorted(missing_orders)}")
                print("   These stages have NO operators currently:")
                
                # Try to find status names for missing orders
                for order in sorted(missing_orders):
                    status = next((st for st in self.status_types 
                                 if st.get('OrderID') == order), None)
                    if status:
                        print(f"     Order {order}: {status.get('Status', 'Unknown')}")
                    else:
                        print(f"     Order {order}: (Status name not found)")
            else:
                print("\n✓ All stages in the range have operators")
        
    def generate_progression_summary(self):
        """Generate summary and recommendations"""
        print("\n" + "=" * 80)
        print("[6/6] PROGRESSION HEALTH SUMMARY")
        print("=" * 80)
        
        # Calculate metrics
        if not self.operators:
            print("\n⚠️  No operator data available for analysis")
            return
        
        orders = []
        for op in self.operators:
            order = op.get('StatusOrderSequence')
            if order and str(order).isdigit():
                orders.append(int(order))
        
        if orders:
            avg_order = sum(orders) / len(orders)
            min_order = min(orders)
            max_order = max(orders)
            
            print(f"\n📈 OVERALL METRICS:")
            print(f"   Average Stage Position: {avg_order:.1f}")
            print(f"   Stage Range: {min_order} to {max_order}")
            print(f"   Lifecycle Spread: {max_order - min_order} stages")
            
            # Health assessment
            print(f"\n🏥 PROGRESSION HEALTH:")
            
            # Check if most operators are stuck early
            early_stage_count = sum(1 for o in orders if o < 5)
            early_pct = early_stage_count / len(orders) * 100
            
            if early_pct > 50:
                print(f"   🚨 CRITICAL: {early_pct:.1f}% of operators in early stages (Order < 5)")
                print("      → Investigate onboarding/credentialing bottlenecks")
            elif early_pct > 30:
                print(f"   ⚠️  WARNING: {early_pct:.1f}% of operators in early stages")
                print("      → Review early-stage processes for efficiency")
            else:
                print(f"   ✓ HEALTHY: Only {early_pct:.1f}% in early stages")
            
            # Check lifecycle completion
            late_stage_count = sum(1 for o in orders if o >= 12)
            late_pct = late_stage_count / len(orders) * 100
            
            print(f"\n   In-Service/Final Stages: {late_pct:.1f}%")
            if late_pct < 10:
                print("      🚨 Very few operators reaching final stages")
                print("      → Review entire lifecycle for blockers")
            elif late_pct < 20:
                print("      ⚠️  Low completion rate to final stages")
            else:
                print("      ✓ Reasonable flow to final stages")
        
        print("\n" + "=" * 80)
        print("RECOMMENDED ACTIONS:")
        print("=" * 80)
        print("1. Focus on bottleneck statuses identified above")
        print("2. Review certification requirements for stuck operators")
        print("3. Investigate missing stage coverage")
        print("4. Run phase3_certification_gaps.py for detailed cert analysis")
        print("=" * 80)
    
    def run(self):
        """Execute full progression analysis"""
        self.load_data()
        self.analyze_status_distribution()
        self.analyze_division_progression()
        self.identify_stuck_operators()
        self.analyze_progression_gaps()
        self.generate_progression_summary()
        
        print(f"\n✓ Progression analysis complete")

if __name__ == '__main__':
    analyzer = ProgressionAnalyzer()
    analyzer.run()
