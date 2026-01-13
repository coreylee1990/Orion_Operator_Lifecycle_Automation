#!/usr/bin/env python3
"""
Operator Status Progression Analysis

Analyzes operator lifecycle progression using StatusTracker data to identify:
- Time spent in each status
- Bottlenecks and delays
- Progression patterns across divisions
- Correlation between certifications and status advancement
"""

import json
from datetime import datetime
from collections import defaultdict
from pathlib import Path

def load_json(filepath):
    """Load JSON data from file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def parse_date(date_str):
    """Parse date string to datetime object"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
    except:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except:
            return None

def get_status_name(status_id, status_types):
    """Get status name from StatusID"""
    for status_type in status_types:
        if status_type['Id'] == status_id:
            return status_type['Status']
    return status_id  # Return ID if name not found

def get_status_order(status_id, status_types):
    """Get status order from StatusID"""
    for status_type in status_types:
        if status_type['Id'] == status_id:
            order = status_type.get('OrderID', '')
            return int(order) if order and order.isdigit() else 999
    return 999

def analyze_operator_journey(operator_id, events, status_types):
    """Analyze individual operator's journey through statuses"""
    # Sort events by date
    sorted_events = sorted(events, key=lambda x: parse_date(x['Date']) or datetime.min)
    
    journey = {
        'operator_id': operator_id,
        'division': sorted_events[0]['DivisionID'] if sorted_events else None,
        'stages': [],
        'total_days': 0,
        'current_status': None
    }
    
    for i, event in enumerate(sorted_events):
        status_name = get_status_name(event['StatusID'], status_types)
        status_order = get_status_order(event['StatusID'], status_types)
        start_date = parse_date(event['Date'])
        
        # Calculate days in status
        if i < len(sorted_events) - 1:
            next_event = sorted_events[i + 1]
            end_date = parse_date(next_event['Date'])
            days_in_status = (end_date - start_date).days if start_date and end_date else 0
        else:
            # Last status - calculate to today
            end_date = datetime.now()
            days_in_status = (end_date - start_date).days if start_date else 0
            journey['current_status'] = status_name
        
        journey['stages'].append({
            'status': status_name,
            'status_id': event['StatusID'],
            'order': status_order,
            'start_date': event['Date'],
            'end_date': end_date.strftime('%Y-%m-%d %H:%M:%S.%f') if i < len(sorted_events) - 1 else 'Current',
            'days_in_status': days_in_status,
            'recorded_by': event['RecordBy']
        })
        
        journey['total_days'] += days_in_status
    
    return journey

def identify_bottlenecks(journeys, status_types):
    """Identify status bottlenecks across all operators"""
    status_times = defaultdict(list)
    status_counts = defaultdict(int)
    
    for journey in journeys:
        for stage in journey['stages']:
            status = stage['status']
            days = stage['days_in_status']
            status_times[status].append(days)
            status_counts[status] += 1
    
    bottlenecks = []
    for status, times in status_times.items():
        if len(times) > 0:
            avg_days = sum(times) / len(times)
            max_days = max(times)
            min_days = min(times)
            
            # Get status order
            status_order = 999
            for st in status_types:
                if st['Status'] == status:
                    order = st.get('OrderID', '')
                    status_order = int(order) if order and order.isdigit() else 999
                    break
            
            bottlenecks.append({
                'status': status,
                'order': status_order,
                'avg_days': round(avg_days, 1),
                'max_days': max_days,
                'min_days': min_days,
                'operator_count': len(times),
                'total_transitions': status_counts[status]
            })
    
    # Sort by average days (descending)
    bottlenecks.sort(key=lambda x: x['avg_days'], reverse=True)
    return bottlenecks

def analyze_cert_completion_by_status(journeys, cert_requirements, operators_data):
    """Analyze when certifications are typically completed relative to status"""
    # Build operator cert lookup - operators_data is a list, not dict with 'operators' key
    operator_certs = {}
    for op in operators_data:
        op_id = op['ID']
        certs = {}
        if 'certifications' in op:
            for cert in op['certifications']:
                cert_name = cert.get('CertType', 'Unknown')
                issue_date = parse_date(cert.get('IssueDate'))
                if issue_date:
                    certs[cert_name] = issue_date
        operator_certs[op_id] = certs
    
    # Analyze cert timing relative to status progression
    cert_status_timing = defaultdict(lambda: {'before': 0, 'during': 0, 'after': 0, 'never': 0})
    
    for journey in journeys:
        op_id = journey['operator_id']
        op_certs = operator_certs.get(op_id, {})
        
        for stage in journey['stages']:
            status = stage['status']
            status_start = parse_date(stage['start_date'])
            status_end = parse_date(stage['end_date']) if stage['end_date'] != 'Current' else datetime.now()
            
            # Get required certs for this status
            status_data = cert_requirements.get(status, {})
            divisions = status_data.get('divisions', {})
            
            # Check all divisions for required certs
            required_certs = set()
            for div_data in divisions.values():
                for cert_info in div_data.get('required', []):
                    required_certs.add(cert_info['cert'])
            
            # Check timing of each required cert
            for cert_name in required_certs:
                cert_date = op_certs.get(cert_name)
                
                if not cert_date:
                    cert_status_timing[f"{status}::{cert_name}"]['never'] += 1
                elif cert_date < status_start:
                    cert_status_timing[f"{status}::{cert_name}"]['before'] += 1
                elif status_start <= cert_date <= status_end:
                    cert_status_timing[f"{status}::{cert_name}"]['during'] += 1
                else:
                    cert_status_timing[f"{status}::{cert_name}"]['after'] += 1
    
    return cert_status_timing

def analyze_division_differences(journeys):
    """Compare progression patterns across divisions"""
    division_stats = defaultdict(lambda: {
        'operators': set(),
        'avg_total_days': [],
        'avg_stages': [],
        'status_times': defaultdict(list)
    })
    
    for journey in journeys:
        division = journey['division']
        if division:
            division_stats[division]['operators'].add(journey['operator_id'])
            division_stats[division]['avg_total_days'].append(journey['total_days'])
            division_stats[division]['avg_stages'].append(len(journey['stages']))
            
            for stage in journey['stages']:
                status = stage['status']
                division_stats[division]['status_times'][status].append(stage['days_in_status'])
    
    # Calculate averages
    division_comparison = []
    for division, stats in division_stats.items():
        total_days_list = stats['avg_total_days']
        stages_list = stats['avg_stages']
        
        comparison = {
            'division': division,
            'operator_count': len(stats['operators']),
            'avg_total_journey_days': round(sum(total_days_list) / len(total_days_list), 1) if total_days_list else 0,
            'avg_stages_count': round(sum(stages_list) / len(stages_list), 1) if stages_list else 0,
            'slowest_status': None,
            'slowest_status_avg_days': 0
        }
        
        # Find slowest status for this division
        for status, times in stats['status_times'].items():
            if times:
                avg_time = sum(times) / len(times)
                if avg_time > comparison['slowest_status_avg_days']:
                    comparison['slowest_status'] = status
                    comparison['slowest_status_avg_days'] = round(avg_time, 1)
        
        division_comparison.append(comparison)
    
    division_comparison.sort(key=lambda x: x['avg_total_journey_days'], reverse=True)
    return division_comparison

def generate_analysis_report(analysis_data, output_dir):
    """Generate comprehensive analysis report"""
    output_file = output_dir / 'status_progression_analysis.json'
    
    with open(output_file, 'w') as f:
        json.dump(analysis_data, f, indent=2, default=str)
    
    return output_file

def generate_text_summary(analysis_data, output_dir):
    """Generate human-readable text summary"""
    output_file = output_dir / 'status_progression_summary.txt'
    
    with open(output_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("OPERATOR STATUS PROGRESSION ANALYSIS\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        # Overview
        f.write(f"Total Operators Analyzed: {analysis_data['summary']['total_operators']}\n")
        f.write(f"Total Status Transitions: {analysis_data['summary']['total_transitions']}\n")
        f.write(f"Divisions Covered: {analysis_data['summary']['divisions_count']}\n")
        f.write(f"Average Journey Duration: {analysis_data['summary']['avg_journey_days']} days\n\n")
        
        # Top Bottlenecks
        f.write("=" * 80 + "\n")
        f.write("TOP BOTTLENECKS (Statuses with Longest Average Duration)\n")
        f.write("=" * 80 + "\n\n")
        
        for i, bottleneck in enumerate(analysis_data['bottlenecks'][:10], 1):
            f.write(f"{i}. {bottleneck['status']}\n")
            f.write(f"   Order: Step {bottleneck['order']}\n")
            f.write(f"   Average Days: {bottleneck['avg_days']}\n")
            f.write(f"   Range: {bottleneck['min_days']} - {bottleneck['max_days']} days\n")
            f.write(f"   Operators Affected: {bottleneck['operator_count']}\n\n")
        
        # Division Comparison
        f.write("=" * 80 + "\n")
        f.write("DIVISION COMPARISON\n")
        f.write("=" * 80 + "\n\n")
        
        for div in analysis_data['division_comparison']:
            f.write(f"Division: {div['division']}\n")
            f.write(f"  Operators: {div['operator_count']}\n")
            f.write(f"  Avg Journey: {div['avg_total_journey_days']} days\n")
            f.write(f"  Avg Stages: {div['avg_stages_count']}\n")
            f.write(f"  Slowest Status: {div['slowest_status']} ({div['slowest_status_avg_days']} days)\n\n")
        
        # Certification Timing Insights
        f.write("=" * 80 + "\n")
        f.write("CERTIFICATION COMPLETION TIMING\n")
        f.write("=" * 80 + "\n\n")
        f.write("Top certifications most often completed DURING status (as intended):\n\n")
        
        # Sort by 'during' count
        timing_list = []
        for key, timing in analysis_data['cert_timing'].items():
            status, cert = key.split('::', 1)
            timing_list.append({
                'status': status,
                'cert': cert,
                'during': timing['during'],
                'before': timing['before'],
                'after': timing['after'],
                'never': timing['never']
            })
        
        timing_list.sort(key=lambda x: x['during'], reverse=True)
        
        for i, item in enumerate(timing_list[:15], 1):
            total = item['during'] + item['before'] + item['after'] + item['never']
            if total > 0:
                during_pct = (item['during'] / total) * 100
                f.write(f"{i}. {item['cert']} @ {item['status']}\n")
                f.write(f"   Completed During: {item['during']} ({during_pct:.1f}%)\n")
                f.write(f"   Before: {item['before']}, After: {item['after']}, Never: {item['never']}\n\n")
        
    return output_file

def main():
    # Set up paths
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / 'data'
    generated_dir = base_dir / 'generated'
    
    print("Loading data files...")
    
    # Load data
    status_tracker = load_json(data_dir / 'pay_StatusTracker.json')
    status_types = load_json(data_dir / 'pay_StatusTypes.txt')
    cert_requirements = load_json(generated_dir / 'cert_requirements_by_status_division.json')
    operators_data = load_json(data_dir / 'pay_Operators.json')
    
    print(f"✓ Loaded {len(status_tracker['statusTracker'])} status tracking events")
    print(f"✓ Loaded {len(status_types)} status types")
    print(f"✓ Loaded certification requirements for {len(cert_requirements)} statuses")
    # operators_data is a list, not a dict
    print(f"✓ Loaded {len(operators_data)} operators")
    
    # Group events by operator
    print("\nGrouping events by operator...")
    operator_events = defaultdict(list)
    for event in status_tracker['statusTracker']:
        operator_events[event['OperatorID']].append(event)
    
    print(f"✓ Found status history for {len(operator_events)} operators")
    
    # Analyze individual journeys
    print("\nAnalyzing operator journeys...")
    journeys = []
    for operator_id, events in operator_events.items():
        journey = analyze_operator_journey(operator_id, events, status_types)
        journeys.append(journey)
    
    print(f"✓ Analyzed {len(journeys)} operator journeys")
    
    # Identify bottlenecks
    print("\nIdentifying bottlenecks...")
    bottlenecks = identify_bottlenecks(journeys, status_types)
    print(f"✓ Identified {len(bottlenecks)} status stages with timing data")
    
    # Analyze division differences
    print("\nAnalyzing division differences...")
    division_comparison = analyze_division_differences(journeys)
    print(f"✓ Compared {len(division_comparison)} divisions")
    
    # Analyze cert completion timing
    print("\nAnalyzing certification completion timing...")
    cert_timing = analyze_cert_completion_by_status(journeys, cert_requirements, operators_data)
    print(f"✓ Analyzed timing for {len(cert_timing)} status-cert combinations")
    
    # Compile analysis data
    analysis_data = {
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'total_operators': len(journeys),
            'total_transitions': sum(len(j['stages']) for j in journeys),
            'divisions_count': len(division_comparison),
            'avg_journey_days': round(sum(j['total_days'] for j in journeys) / len(journeys), 1) if journeys else 0
        },
        'bottlenecks': bottlenecks,
        'division_comparison': division_comparison,
        'cert_timing': {k: dict(v) for k, v in cert_timing.items()},
        'operator_journeys': journeys
    }
    
    # Generate reports
    print("\nGenerating reports...")
    json_file = generate_analysis_report(analysis_data, generated_dir)
    text_file = generate_text_summary(analysis_data, generated_dir)
    
    print(f"\n✓ Analysis complete!")
    print(f"✓ JSON report: {json_file}")
    print(f"✓ Text summary: {text_file}")
    
    # Print quick summary
    print("\n" + "=" * 80)
    print("QUICK SUMMARY")
    print("=" * 80)
    print(f"\nTop 3 Bottlenecks:")
    for i, b in enumerate(bottlenecks[:3], 1):
        print(f"  {i}. {b['status']}: {b['avg_days']} days average (Step {b['order']})")
    
    print(f"\nSlowest Division: {division_comparison[0]['division']}")
    print(f"  Average Journey: {division_comparison[0]['avg_total_journey_days']} days")
    
    print(f"\nFastest Division: {division_comparison[-1]['division']}")
    print(f"  Average Journey: {division_comparison[-1]['avg_total_journey_days']} days")

if __name__ == '__main__':
    main()
