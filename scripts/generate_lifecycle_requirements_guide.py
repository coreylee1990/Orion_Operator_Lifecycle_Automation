#!/usr/bin/env python3
"""
Generate Operator Lifecycle Requirements Guide

Creates a comprehensive guide showing:
- Each lifecycle step in order
- Required certifications at each step (80%+ adoption)
- Common certifications (50-79% adoption)
- Division-specific variations
"""

import json
from pathlib import Path
from collections import defaultdict

def load_json(filepath):
    """Load JSON data from file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def main():
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / 'data'
    generated_dir = base_dir / 'generated'
    
    print("Loading certification requirements data...")
    cert_reqs = load_json(generated_dir / 'cert_requirements_by_status_division.json')
    
    # Group statuses by order
    statuses_by_order = defaultdict(list)
    for status, data in cert_reqs.items():
        order = data.get('order', '')
        if order and order != '':
            statuses_by_order[order].append({
                'status': status,
                'divisions': data['divisions']
            })
    
    # Sort orders
    sorted_orders = sorted(statuses_by_order.keys(), key=lambda x: int(x) if x.isdigit() else 999)
    
    # Build the guide
    output_file = generated_dir / 'OPERATOR_LIFECYCLE_REQUIREMENTS_GUIDE.md'
    
    with open(output_file, 'w') as f:
        f.write("# Operator Lifecycle Requirements Guide\n\n")
        f.write("**Complete certification requirements from start to finish**\n\n")
        f.write(f"Generated: January 11, 2026\n")
        f.write(f"Data Source: {len(cert_reqs)} statuses analyzed across all divisions\n\n")
        
        f.write("---\n\n")
        f.write("## How to Read This Guide\n\n")
        f.write("**Certification Adoption Levels:**\n")
        f.write("- 🔴 **REQUIRED (80%+ adoption)** - Most operators have this certification\n")
        f.write("- 🟡 **COMMON (50-79% adoption)** - Many operators have this certification\n")
        f.write("- ⚪ **OPTIONAL (<50% adoption)** - Some operators have this certification\n\n")
        f.write("**Note:** These requirements are inferred from actual operator data, showing what certifications ")
        f.write("operators typically have at each status. Division-specific requirements may vary.\n\n")
        
        f.write("---\n\n")
        f.write("## 📋 Quick Reference: Complete Lifecycle\n\n")
        
        # Build quick reference
        for order in sorted_orders:
            if order.isdigit() and int(order) < 90:  # Exclude high order numbers (out of service, etc)
                statuses = statuses_by_order[order]
                status_names = [s['status'] for s in statuses]
                f.write(f"**Step {order}:** {' / '.join(status_names)}\n\n")
        
        f.write("\n---\n\n")
        f.write("## 📊 Detailed Requirements by Step\n\n")
        
        # Detailed breakdown
        for order in sorted_orders:
            if not order.isdigit() or int(order) >= 90:
                continue  # Skip non-main lifecycle statuses
            
            statuses = statuses_by_order[order]
            
            f.write(f"### Step {order}: {' / '.join([s['status'] for s in statuses])}\n\n")
            
            # Get all certifications across all divisions for this status
            for status_data in statuses:
                status_name = status_data['status']
                divisions = status_data['divisions']
                
                if len(statuses) > 1:
                    f.write(f"#### {status_name}\n\n")
                
                # Aggregate certifications across divisions
                all_required = defaultdict(list)
                all_common = defaultdict(list)
                all_optional = defaultdict(list)
                
                for div_name, div_data in divisions.items():
                    for cert in div_data.get('required', []):
                        all_required[cert['cert']].append({
                            'division': div_name,
                            'percentage': cert['percentage']
                        })
                    for cert in div_data.get('common', []):
                        all_common[cert['cert']].append({
                            'division': div_name,
                            'percentage': cert['percentage']
                        })
                    for cert in div_data.get('optional', []):
                        all_optional[cert['cert']].append({
                            'division': div_name,
                            'percentage': cert['percentage']
                        })
                
                # Write required certs
                if all_required:
                    f.write("**🔴 REQUIRED CERTIFICATIONS (80%+ adoption)**\n\n")
                    for cert_name, divisions_list in sorted(all_required.items()):
                        if len(divisions_list) == len(divisions):
                            # All divisions require this
                            avg_pct = sum(d['percentage'] for d in divisions_list) / len(divisions_list)
                            f.write(f"- **{cert_name}** ({avg_pct:.0f}% adoption across all divisions)\n")
                        else:
                            # Some divisions require this
                            div_names = [d['division'] for d in divisions_list]
                            f.write(f"- **{cert_name}** (Required in: {', '.join(div_names)})\n")
                    f.write("\n")
                
                # Write common certs
                if all_common:
                    f.write("**🟡 COMMON CERTIFICATIONS (50-79% adoption)**\n\n")
                    for cert_name, divisions_list in sorted(all_common.items()):
                        div_names = [d['division'] for d in divisions_list]
                        avg_pct = sum(d['percentage'] for d in divisions_list) / len(divisions_list)
                        f.write(f"- {cert_name} ({avg_pct:.0f}% adoption)\n")
                    f.write("\n")
                
                # Write optional certs (only if not too many)
                if all_optional and len(all_optional) < 20:
                    f.write("**⚪ OPTIONAL CERTIFICATIONS (<50% adoption)**\n\n")
                    for cert_name in sorted(all_optional.keys())[:10]:  # Limit to top 10
                        f.write(f"- {cert_name}\n")
                    if len(all_optional) > 10:
                        f.write(f"- _{len(all_optional) - 10} more optional certifications..._\n")
                    f.write("\n")
                
                # Add division-specific notes
                if len(divisions) > 1:
                    f.write(f"**Divisions analyzed:** {', '.join(sorted(divisions.keys()))}\n\n")
                
                f.write("---\n\n")
        
        # Add appendix with division differences
        f.write("## 📍 Division-Specific Variations\n\n")
        f.write("Some certifications are only required in specific divisions. Here are the key differences:\n\n")
        
        # Collect division-specific requirements
        division_specific = defaultdict(lambda: defaultdict(list))
        
        for order in sorted_orders:
            if not order.isdigit() or int(order) >= 90:
                continue
            
            for status_data in statuses_by_order[order]:
                status_name = status_data['status']
                divisions = status_data['divisions']
                
                # Find certs that appear in some but not all divisions
                cert_divisions = defaultdict(set)
                for div_name, div_data in divisions.items():
                    for cert in div_data.get('required', []):
                        cert_divisions[cert['cert']].add(div_name)
                
                for cert_name, div_set in cert_divisions.items():
                    if len(div_set) < len(divisions) and len(div_set) > 0:
                        # This cert is division-specific
                        for div in div_set:
                            division_specific[div][status_name].append(cert_name)
        
        if division_specific:
            for division in sorted(division_specific.keys()):
                f.write(f"### {division}\n\n")
                for status, certs in sorted(division_specific[division].items()):
                    f.write(f"**{status}:**\n")
                    for cert in certs:
                        f.write(f"- {cert}\n")
                    f.write("\n")
        else:
            f.write("_No significant division-specific variations found. Requirements are consistent across divisions._\n\n")
        
        # Add timing information
        f.write("---\n\n")
        f.write("## ⏱️ Estimated Time in Each Step\n\n")
        f.write("Based on StatusTracker progression analysis:\n\n")
        
        # Hard-code the timing data from our analysis
        timing_data = {
            "1": {"status": "REGISTRATION", "avg_days": 11.2, "range": "0-90"},
            "2": {"status": "ONBOARDING / COMPLIANCE REVIEW", "avg_days": 15.4, "range": "0-409"},
            "3": {"status": "CREDENTIALING", "avg_days": 8.2, "range": "0-80"},
            "4": {"status": "DOT SCREENING", "avg_days": 10.5, "range": "0-50"},
            "5": {"status": "ORIENTATION / IN-SERVICE", "avg_days": 70.1, "range": "0-314"},
            "12": {"status": "APPROVED FOR CONTRACTING", "avg_days": 230.0, "range": "9-662"},
        }
        
        for step, data in timing_data.items():
            f.write(f"**Step {step} - {data['status']}**\n")
            f.write(f"- Average: {data['avg_days']} days\n")
            f.write(f"- Range: {data['range']} days\n\n")
        
        f.write("⚠️ **Note:** Step 12 (APPROVED FOR CONTRACTING) shows significant delays (230 days average). ")
        f.write("This is a critical bottleneck requiring investigation.\n\n")
        
        # Add methodology
        f.write("---\n\n")
        f.write("## 📊 Methodology\n\n")
        f.write("This guide is generated from real operator data:\n\n")
        f.write("- **81 operators** across all lifecycle stages\n")
        f.write("- **4,731 certification records** analyzed\n")
        f.write("- **200 status progression events** tracked\n")
        f.write("- **7 divisions** represented\n\n")
        f.write("**Requirement Thresholds:**\n")
        f.write("- **REQUIRED:** 80%+ of operators at this status have this certification\n")
        f.write("- **COMMON:** 50-79% of operators have this certification\n")
        f.write("- **OPTIONAL:** <50% of operators have this certification\n\n")
        f.write("These thresholds are data-driven and reflect actual practices across Orion divisions.\n\n")
        
        f.write("---\n\n")
        f.write("**For detailed analysis, see:**\n")
        f.write("- [Status Progression Analysis](status_progression_summary.txt)\n")
        f.write("- [Progression & Certification Correlation](PROGRESSION_CERT_CORRELATION_ANALYSIS.md)\n")
        f.write("- [Complete Solution Summary](../COMPLETE_SOLUTION_SUMMARY.md)\n")
    
    print(f"\n✓ Guide generated: {output_file}")
    print(f"✓ Lifecycle steps documented: {len([o for o in sorted_orders if o.isdigit() and int(o) < 90])}")
    
    # Print quick summary
    print("\n" + "="*80)
    print("LIFECYCLE STEPS SUMMARY")
    print("="*80 + "\n")
    
    for order in sorted_orders:
        if order.isdigit() and int(order) < 90:
            statuses = statuses_by_order[order]
            status_names = ' / '.join([s['status'] for s in statuses])
            print(f"Step {order}: {status_names}")

if __name__ == '__main__':
    main()
