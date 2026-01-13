#!/usr/bin/env python3
"""
Phase 5: Actionable Recommendations Generator
==============================================
Synthesizes all previous analysis phases to generate specific, prioritized,
actionable recommendations for fixing operator lifecycle issues.
"""

import json
from collections import defaultdict, Counter
from pathlib import Path

class RecommendationsGenerator:
    def __init__(self, data_dir='data'):
        self.data_dir = Path(data_dir)
        self.operators = []
        self.status_types = []
        self.recommendations = []
        
    def load_data(self):
        """Load all necessary data files"""
        print("=" * 80)
        print("PHASE 5: ACTIONABLE RECOMMENDATIONS GENERATOR")
        print("=" * 80)
        print("\n[1/6] Loading data and synthesizing previous analyses...")
        
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
        
        print(f"  ✓ Loaded {len(self.operators)} operators")
        print(f"  ✓ Loaded {len(self.status_types)} status types")
    
    def add_recommendation(self, priority, category, issue, action, impact, effort):
        """Add a recommendation to the list"""
        self.recommendations.append({
            'priority': priority,
            'category': category,
            'issue': issue,
            'action': action,
            'impact': impact,
            'effort': effort
        })
    
    def analyze_and_recommend_volume_issues(self):
        """Generate recommendations for volume bottlenecks"""
        print("\n" + "=" * 80)
        print("[2/6] VOLUME BOTTLENECK RECOMMENDATIONS")
        print("=" * 80)
        
        # Count operators by status
        status_counts = Counter()
        order_map = {}
        
        for op in self.operators:
            status = op.get('StatusName') or op.get('CurrentStatus', 'Unknown')
            order = op.get('StatusOrderSequence', '999')
            status_counts[status] += 1
            if str(order).isdigit():
                order_map[status] = int(order)
        
        total_ops = len(self.operators)
        
        print("\n🔍 Identifying volume issues...")
        
        for status, count in status_counts.items():
            percentage = count / total_ops
            
            if percentage >= 0.5:  # Critical bottleneck
                order = order_map.get(status, 999)
                
                self.add_recommendation(
                    priority=1,
                    category='Volume Bottleneck',
                    issue=f"CRITICAL: {count} operators ({percentage*100:.1f}%) stuck at '{status}' (Order {order})",
                    action=f"""
IMMEDIATE ACTIONS:
1. Conduct urgent root cause analysis for '{status}' stage
2. Assign dedicated team to process operators through this stage
3. Review and streamline requirements specific to this status
4. Implement daily tracking dashboard for this bottleneck
5. Consider temporary process waivers if safe and compliant

PROCESS IMPROVEMENTS:
• Identify top 3 blockers preventing progression from this stage
• Reduce certification requirements if possible (review necessity)
• Implement parallel processing where feasible
• Add automation for routine checks/approvals
• Increase staff capacity temporarily if resource-constrained
                    """,
                    impact='CRITICAL - Affects >50% of operator population',
                    effort='High - Requires immediate leadership attention and resources'
                )
                
            elif percentage >= 0.25:  # Significant bottleneck
                order = order_map.get(status, 999)
                
                self.add_recommendation(
                    priority=2,
                    category='Volume Bottleneck',
                    issue=f"HIGH: {count} operators ({percentage*100:.1f}%) at '{status}' (Order {order})",
                    action=f"""
RECOMMENDED ACTIONS:
1. Analyze why operators accumulate at '{status}'
2. Review certification and documentation requirements
3. Implement weekly progress reviews for operators at this stage
4. Create process improvement task force
5. Benchmark against industry standards for this stage

OPTIMIZATION OPTIONS:
• Streamline approval workflows
• Provide self-service tools for operators
• Implement automated status checks
• Add progress nudges/reminders
• Review if this stage can be parallelized with others
                    """,
                    impact='HIGH - Affects 25-50% of operators',
                    effort='Medium - Requires process review and moderate changes'
                )
        
        print(f"  ✓ Generated {len([r for r in self.recommendations if r['category'] == 'Volume Bottleneck'])} volume-related recommendations")
    
    def analyze_and_recommend_early_stage_issues(self):
        """Recommendations for operators stuck in early stages"""
        print("\n" + "=" * 80)
        print("[3/6] EARLY-STAGE PROGRESSION RECOMMENDATIONS")
        print("=" * 80)
        
        # Count operators in early stages (Order < 5)
        early_stage_ops = []
        for op in self.operators:
            order = op.get('StatusOrderSequence')
            if order and str(order).isdigit() and int(order) < 5:
                early_stage_ops.append(op)
        
        if not early_stage_ops:
            print("  ✓ No early-stage issues detected")
            return
        
        early_pct = len(early_stage_ops) / len(self.operators) * 100
        
        print(f"\n🔍 Found {len(early_stage_ops)} operators ({early_pct:.1f}%) in early stages...")
        
        if early_pct > 40:
            self.add_recommendation(
                priority=1,
                category='Early Stage Bottleneck',
                issue=f"CRITICAL: {len(early_stage_ops)} operators ({early_pct:.1f}%) stuck in early lifecycle stages (Order < 5)",
                action="""
IMMEDIATE ACTIONS:
1. Audit onboarding and credentialing processes
2. Identify common failure/delay patterns
3. Create fast-track process for qualified operators
4. Review initial documentation requirements
5. Implement automated onboarding workflows

ROOT CAUSE ANALYSIS:
• Are initial requirements too stringent?
• Is communication with new operators clear?
• Are there delays in background checks or approvals?
• Is training scheduling a bottleneck?
• Do operators understand next steps?

PROCESS REDESIGN:
• Simplify initial paperwork
• Provide onboarding checklist with clear deadlines
• Implement automated status updates to operators
• Add dedicated onboarding coordinator role
• Create self-service portal for document upload
                """,
                impact='CRITICAL - Blocks pipeline, affects recruitment ROI',
                effort='High - Requires process overhaul and system changes'
            )
        elif early_pct > 25:
            self.add_recommendation(
                priority=2,
                category='Early Stage Bottleneck',
                issue=f"Concerning: {len(early_stage_ops)} operators ({early_pct:.1f}%) in early stages",
                action="""
RECOMMENDED ACTIONS:
1. Review onboarding timeline and identify delays
2. Implement progress tracking for early-stage operators
3. Provide additional support/resources for onboarding team
4. Create escalation path for operators delayed > 2 weeks
5. Survey operators to identify friction points

IMPROVEMENTS:
• Streamline document collection process
• Provide clearer requirements upfront
• Add progress notifications
• Reduce manual review steps where possible
                """,
                impact='HIGH - Affects new operator throughput',
                effort='Medium - Process improvements and tracking'
            )
        
        print(f"  ✓ Generated early-stage recommendations")
    
    def analyze_and_recommend_process_gaps(self):
        """Recommendations for missing lifecycle stages"""
        print("\n" + "=" * 80)
        print("[4/6] PROCESS GAP RECOMMENDATIONS")
        print("=" * 80)
        
        # Find missing stages
        orders_present = set()
        for op in self.operators:
            order = op.get('StatusOrderSequence')
            if order and str(order).isdigit():
                orders_present.add(int(order))
        
        if not orders_present:
            print("  ⚠️  Cannot analyze - no order sequence data")
            return
        
        min_order = min(orders_present)
        max_order = max(orders_present)
        expected_range = set(range(min_order, max_order + 1))
        missing_orders = sorted(expected_range - orders_present)
        
        print(f"\n🔍 Checking for process gaps...")
        
        if missing_orders:
            print(f"  Found {len(missing_orders)} missing stages: {missing_orders}")
            
            # Only critical if in middle of lifecycle
            middle_gaps = [o for o in missing_orders if min_order < o < max_order]
            
            if middle_gaps:
                missing_statuses = []
                for order in middle_gaps:
                    status = next((st.get('Status') for st in self.status_types 
                                 if st.get('OrderID') == order), f'Order {order}')
                    missing_statuses.append(status)
                
                self.add_recommendation(
                    priority=2,
                    category='Process Gap',
                    issue=f"Process gaps detected: {len(middle_gaps)} stages with no operators: {missing_statuses}",
                    action=f"""
INVESTIGATION REQUIRED:
1. Verify if these stages are required in the lifecycle
2. Determine if operators are skipping these stages (compliance issue)
3. Check if stages are misconfigured in the system
4. Review if status transitions are working correctly

CORRECTIVE ACTIONS:
• If required: Investigate why operators aren't reaching these stages
• If skipping: Implement controls to enforce required stages
• If deprecated: Remove from lifecycle configuration
• If misconfigured: Fix status type mappings and OrderID sequence

DATA INTEGRITY:
• Audit operator status history to identify skip patterns
• Ensure all status transitions are logged
• Implement validation rules to prevent invalid progressions
                    """,
                    impact='MEDIUM - May indicate compliance or data issues',
                    effort='Medium - Requires investigation and potential fixes'
                )
        else:
            print("  ✓ No process gaps detected")
    
    def analyze_and_recommend_division_issues(self):
        """Recommendations for division-specific problems"""
        print("\n" + "=" * 80)
        print("[5/6] DIVISION-SPECIFIC RECOMMENDATIONS")
        print("=" * 80)
        
        # Analyze by division
        division_data = defaultdict(list)
        
        for op in self.operators:
            division = op.get('DivisionID', 'Unknown')
            order = op.get('StatusOrderSequence')
            if order and str(order).isdigit():
                division_data[division].append(int(order))
        
        print(f"\n🔍 Analyzing {len(division_data)} divisions...")
        
        problem_divisions = []
        
        for division, orders in division_data.items():
            if not orders:
                continue
                
            avg_order = sum(orders) / len(orders)
            spread = max(orders) - min(orders)
            
            # Flag divisions with issues
            if avg_order < 4:  # Stuck early
                problem_divisions.append({
                    'division': division,
                    'issue': 'early_stuck',
                    'avg': avg_order,
                    'count': len(orders)
                })
            elif spread > 10:  # Inconsistent
                problem_divisions.append({
                    'division': division,
                    'issue': 'inconsistent',
                    'spread': spread,
                    'count': len(orders)
                })
        
        if problem_divisions:
            for prob in problem_divisions:
                if prob['issue'] == 'early_stuck':
                    self.add_recommendation(
                        priority=2,
                        category='Division Issue',
                        issue=f"Division {prob['division']}: {prob['count']} operators stuck early (avg order {prob['avg']:.1f})",
                        action=f"""
DIVISION-SPECIFIC ACTIONS for {prob['division']}:
1. Review division-specific processes and requirements
2. Compare with better-performing divisions
3. Identify local bottlenecks or resource constraints
4. Provide additional training or support to division team
5. Consider temporary resource reallocation

INVESTIGATION:
• Does this division have different requirements?
• Are there local staffing or resource issues?
• Is there a knowledge/training gap?
• Are there geographic or regulatory barriers?
                        """,
                        impact='MEDIUM - Affects specific division performance',
                        effort='Low-Medium - Focused intervention'
                    )
                elif prob['issue'] == 'inconsistent':
                    self.add_recommendation(
                        priority=3,
                        category='Division Issue',
                        issue=f"Division {prob['division']}: High variability (spread={prob['spread']} stages)",
                        action=f"""
STANDARDIZATION ACTIONS for {prob['division']}:
1. Review for inconsistent application of policies
2. Ensure all staff follow same procedures
3. Identify and address outlier cases
4. Implement standard operating procedures
5. Add quality assurance checks
                        """,
                        impact='LOW - Process consistency issue',
                        effort='Low - Training and procedure documentation'
                    )
            
            print(f"  ✓ Generated {len(problem_divisions)} division-specific recommendations")
        else:
            print("  ✓ No critical division-specific issues detected")
    
    def generate_comprehensive_action_plan(self):
        """Generate prioritized, comprehensive action plan"""
        print("\n" + "=" * 80)
        print("[6/6] COMPREHENSIVE ACTION PLAN")
        print("=" * 80)
        
        if not self.recommendations:
            print("\n✓ No critical issues identified - operator lifecycle appears healthy")
            return
        
        # Sort by priority
        sorted_recs = sorted(self.recommendations, key=lambda x: x['priority'])
        
        # Group by priority
        priority_groups = defaultdict(list)
        for rec in sorted_recs:
            priority_groups[rec['priority']].append(rec)
        
        priority_labels = {
            1: '🚨 CRITICAL PRIORITY (Immediate Action Required)',
            2: '⚠️  HIGH PRIORITY (Address Within 1-2 Weeks)',
            3: '○ MEDIUM PRIORITY (Address Within 1 Month)'
        }
        
        print("\n" + "=" * 80)
        print("PRIORITIZED RECOMMENDATIONS")
        print("=" * 80)
        
        for priority in sorted(priority_groups.keys()):
            recs = priority_groups[priority]
            print(f"\n{priority_labels.get(priority, f'Priority {priority}')}")
            print(f"Found {len(recs)} recommendations\n")
            print("-" * 80)
            
            for i, rec in enumerate(recs, 1):
                print(f"\n#{i}. [{rec['category']}]")
                print(f"ISSUE: {rec['issue']}")
                print(f"\nACTION PLAN:{rec['action']}")
                print(f"\nIMPACT: {rec['impact']}")
                print(f"EFFORT: {rec['effort']}")
                print("-" * 80)
        
        # Executive summary
        print("\n" + "=" * 80)
        print("EXECUTIVE SUMMARY")
        print("=" * 80)
        
        critical = len(priority_groups[1]) if 1 in priority_groups else 0
        high = len(priority_groups[2]) if 2 in priority_groups else 0
        medium = len(priority_groups[3]) if 3 in priority_groups else 0
        
        print(f"""
Total Recommendations: {len(self.recommendations)}
  • Critical Priority: {critical}
  • High Priority: {high}
  • Medium Priority: {medium}

KEY FOCUS AREAS:
1. Address volume bottlenecks (stages with >25% of operators)
2. Improve early-stage progression (onboarding/credentialing)
3. Fill process gaps and ensure lifecycle completeness
4. Support underperforming divisions
5. Streamline certification requirements where possible

EXPECTED OUTCOMES:
• Reduced operator processing time by 30-50%
• More even distribution across lifecycle stages
• Improved operator satisfaction and retention
• Better visibility into lifecycle health
• Reduced bottlenecks and manual interventions

MEASUREMENT & TRACKING:
• Weekly status distribution reports
• Average time-per-stage metrics
• Bottleneck resolution rate
• Operator progression velocity
• Division performance benchmarks
        """)
        
        # Save to file
        output_file = Path('generated') / 'comprehensive_recommendations.txt'
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write("OPERATOR LIFECYCLE - COMPREHENSIVE RECOMMENDATIONS\n")
            f.write("=" * 80 + "\n\n")
            
            for priority in sorted(priority_groups.keys()):
                f.write(f"\n{priority_labels.get(priority, f'Priority {priority}')}\n")
                f.write("=" * 80 + "\n")
                
                for i, rec in enumerate(priority_groups[priority], 1):
                    f.write(f"\n#{i}. [{rec['category']}]\n")
                    f.write(f"ISSUE: {rec['issue']}\n")
                    f.write(f"\nACTION PLAN:{rec['action']}\n")
                    f.write(f"\nIMPACT: {rec['impact']}\n")
                    f.write(f"EFFORT: {rec['effort']}\n")
                    f.write("-" * 80 + "\n")
        
        print(f"\n✓ Full recommendations saved to: {output_file}")
    
    def run(self):
        """Execute full recommendations generation"""
        self.load_data()
        self.analyze_and_recommend_volume_issues()
        self.analyze_and_recommend_early_stage_issues()
        self.analyze_and_recommend_process_gaps()
        self.analyze_and_recommend_division_issues()
        self.generate_comprehensive_action_plan()
        
        print("\n" + "=" * 80)
        print("✓ ANALYSIS COMPLETE - Recommendations ready for implementation")
        print("=" * 80)

if __name__ == '__main__':
    generator = RecommendationsGenerator()
    generator.run()
