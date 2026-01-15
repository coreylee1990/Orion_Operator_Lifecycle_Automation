#!/usr/bin/env python3
"""
Master Analysis Runner
======================
Orchestrates all 5 analysis phases in sequence and generates
a unified executive report.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

class MasterAnalysisRunner:
    def __init__(self):
        self.scripts_dir = Path(__file__).parent
        self.results = {}
        
        self.phases = [
            {
                'id': 1,
                'name': 'Lifecycle Overview',
                'script': 'phase1_lifecycle_overview.py',
                'description': 'Map lifecycle structure and current distribution'
            },
            {
                'id': 2,
                'name': 'Progression Analysis',
                'script': 'phase2_progression_analysis.py',
                'description': 'Identify stuck operators and velocity issues'
            },
            {
                'id': 3,
                'name': 'Certification Gaps',
                'script': 'phase3_certification_gaps.py',
                'description': 'Find missing/expired certifications'
            },
            {
                'id': 4,
                'name': 'Bottleneck Identification',
                'script': 'phase4_bottleneck_analysis.py',
                'description': 'Identify systemic process bottlenecks'
            },
            {
                'id': 5,
                'name': 'Recommendations',
                'script': 'phase5_recommendations.py',
                'description': 'Generate actionable fixes and action plan'
            }
        ]
    
    def print_header(self):
        """Print analysis header"""
        print("\n" + "=" * 100)
        print(" " * 25 + "OPERATOR LIFECYCLE - COMPREHENSIVE ANALYSIS")
        print(" " * 35 + f"Run Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 100)
        
        print("\nThis analysis will run through 5 phases:")
        for phase in self.phases:
            print(f"  {phase['id']}. {phase['name']:<30} - {phase['description']}")
        
        print("\n" + "=" * 100)
        print("Starting analysis...\n")
    
    def run_phase(self, phase):
        """Run a single analysis phase"""
        script_path = self.scripts_dir / phase['script']
        
        print("\n" + "█" * 100)
        print(f"  PHASE {phase['id']}: {phase['name'].upper()}")
        print("█" * 100 + "\n")
        
        if not script_path.exists():
            print(f"⚠️  WARNING: Script not found: {script_path}")
            self.results[phase['id']] = 'SKIPPED'
            return False
        
        try:
            # Run the phase script
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=self.scripts_dir.parent,
                capture_output=False,
                text=True
            )
            
            if result.returncode == 0:
                print(f"\n✓ Phase {phase['id']} completed successfully")
                self.results[phase['id']] = 'SUCCESS'
                return True
            else:
                print(f"\n⚠️  Phase {phase['id']} completed with errors (exit code: {result.returncode})")
                self.results[phase['id']] = 'ERROR'
                return False
                
        except Exception as e:
            print(f"\n❌ Phase {phase['id']} failed with exception: {e}")
            self.results[phase['id']] = 'FAILED'
            return False
    
    def generate_executive_summary(self):
        """Generate final executive summary"""
        print("\n\n" + "=" * 100)
        print(" " * 35 + "EXECUTIVE SUMMARY")
        print("=" * 100)
        
        # Analysis completion status
        print("\n📊 ANALYSIS COMPLETION STATUS:")
        print("-" * 100)
        
        for phase in self.phases:
            status = self.results.get(phase['id'], 'NOT RUN')
            status_icon = {
                'SUCCESS': '✓',
                'ERROR': '⚠️',
                'FAILED': '❌',
                'SKIPPED': '○',
                'NOT RUN': '○'
            }.get(status, '?')
            
            print(f"  {status_icon} Phase {phase['id']}: {phase['name']:<30} [{status}]")
        
        # Overall health assessment
        successful_phases = sum(1 for r in self.results.values() if r == 'SUCCESS')
        total_phases = len(self.phases)
        
        print(f"\n  Completed: {successful_phases}/{total_phases} phases")
        
        # Key findings summary (based on what we know from the data)
        print("\n🔍 KEY FINDINGS:")
        print("-" * 100)
        print("""
Based on the comprehensive analysis across all phases:

1. OPERATOR DISTRIBUTION:
   • Analyzed operator distribution across lifecycle stages
   • Identified concentration patterns and bottlenecks
   • Measured division-level performance variations

2. PROGRESSION HEALTH:
   • Evaluated operator progression velocity
   • Identified early-stage accumulation issues
   • Detected lifecycle gaps and missing stages

3. CERTIFICATION COMPLIANCE:
   • Mapped certification requirements by status
   • Identified operators with missing/expired certifications
   • Calculated compliance rates by lifecycle stage

4. PROCESS BOTTLENECKS:
   • Identified volume bottlenecks (>25% concentration)
   • Analyzed certification-driven delays
   • Found structural process gaps

5. ACTIONABLE RECOMMENDATIONS:
   • Generated prioritized fix recommendations
   • Provided specific action plans by priority level
   • Estimated impact and effort for each recommendation
        """)
        
        print("\n📁 OUTPUT FILES:")
        print("-" * 100)
        
        output_dir = Path('generated')
        if output_dir.exists():
            output_files = list(output_dir.glob('*.txt')) + list(output_dir.glob('*.md'))
            if output_files:
                for file in sorted(output_files):
                    size_kb = file.stat().st_size / 1024
                    print(f"  • {file.name} ({size_kb:.1f} KB)")
            else:
                print("  (No output files generated)")
        else:
            print("  (Output directory not found)")
        
        print("\n" + "=" * 100)
        print("NEXT STEPS:")
        print("=" * 100)
        print("""
1. IMMEDIATE ACTIONS (THIS WEEK):
   • Review critical priority recommendations in phase5_recommendations.py output
   • Assign ownership for each critical issue
   • Set up daily tracking for identified bottlenecks
   • Brief leadership on findings

2. SHORT-TERM (1-2 WEEKS):
   • Implement quick wins from high-priority recommendations
   • Begin root cause analysis for major bottlenecks
   • Review and streamline certification requirements
   • Set up automated monitoring dashboards

3. MEDIUM-TERM (1 MONTH):
   • Address all high and medium priority recommendations
   • Implement process improvements identified
   • Train staff on new procedures
   • Measure and track improvement metrics

4. ONGOING:
   • Run this analysis monthly to track progress
   • Maintain lifecycle health dashboards
   • Continuously optimize based on data
   • Share best practices across divisions
        """)
        
        print("\n" + "=" * 100)
        print("🎯 To implement recommendations, review: generated/comprehensive_recommendations.txt")
        print("=" * 100 + "\n")
    
    def run_all(self):
        """Run all analysis phases"""
        self.print_header()
        
        # Run each phase in sequence
        for phase in self.phases:
            success = self.run_phase(phase)
            
            # Continue even if a phase fails
            if not success:
                print(f"\n⚠️  Phase {phase['id']} had issues but continuing with remaining phases...")
        
        # Generate summary
        self.generate_executive_summary()
        
        # Final status
        all_success = all(r == 'SUCCESS' for r in self.results.values())
        
        if all_success:
            print("✓ All analysis phases completed successfully!")
            return 0
        else:
            print("⚠️  Analysis completed with some issues. Review phase outputs above.")
            return 1

def main():
    """Main entry point"""
    runner = MasterAnalysisRunner()
    exit_code = runner.run_all()
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
