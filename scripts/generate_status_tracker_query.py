#!/usr/bin/env python3
"""
Generate SQL query to fetch StatusTracker data for operators in our dataset.
"""

import json
from pathlib import Path

def generate_status_tracker_query():
    """Generate SQL query with operator IDs from our operators data."""
    
    # Load operators data
    operators_file = Path(__file__).parent.parent / 'data' / 'pay_Operators.json'
    
    print(f"Loading operators from: {operators_file}")
    
    with open(operators_file, 'r', encoding='utf-8') as f:
        operators_data = json.load(f)
    
    # Extract operator IDs
    if isinstance(operators_data, dict):
        operators = operators_data.get('operators', [])
    else:
        operators = operators_data
    
    operator_ids = [op['ID'] for op in operators if 'ID' in op]
    
    print(f"✓ Found {len(operator_ids)} operators")
    
    # Generate SQL query
    operator_id_lines = ",\n        ".join([f"'{op_id}'" for op_id in operator_ids])
    
    sql_query = f"""-- Get StatusTracker records for operators in our dataset
-- Generated query with {len(operator_ids)} operator IDs

SELECT 
    ID,
    StatusID,
    OperatorID,
    Date,
    RecordAt,
    RecordBy,
    UpdateAt,
    UpdateBy,
    DivisionID,
    SequenceID,
    ProviderID,
    FleetID
FROM pay_StatusTracker
WHERE 
    OperatorID IN (
        {operator_id_lines}
    )
ORDER BY 
    OperatorID,
    SequenceID,
    Date,
    RecordAt;
"""
    
    # Save query to file
    output_file = Path(__file__).parent / 'get_status_tracker_data.sql'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql_query)
    
    print(f"✓ Generated SQL query: {output_file}")
    print(f"✓ Query includes {len(operator_ids)} operator IDs")
    print("\nQuery preview (first 50 lines):")
    print("=" * 80)
    print('\n'.join(sql_query.split('\n')[:50]))
    
    if len(sql_query.split('\n')) > 50:
        print("... (truncated)")

if __name__ == '__main__':
    generate_status_tracker_query()
