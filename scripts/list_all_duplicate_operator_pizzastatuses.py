import json
from collections import defaultdict

with open('data/pay_PizzaStatuses.json', 'r', encoding='utf-8') as f:
    statuses = json.load(f)

# Find operator statuses
operator_statuses = [s for s in statuses if s.get('IsOperator') is True]

# Group by Status name
status_groups = defaultdict(list)
for s in operator_statuses:
    status_groups[s['Status'].strip()].append(s)

duplicates = {k: v for k, v in status_groups.items() if len(v) > 1}

if not duplicates:
    print('No duplicate operator statuses found.')
else:
    print('Detailed list of all duplicate Operator PizzaStatuses:')
    for name, group in duplicates.items():
        print(f'\nStatus: {name} (Total: {len(group)})')
        for i, s in enumerate(group, 1):
            print(f'  Version {i}:')
            for k, v in s.items():
                print(f'    {k}: {v}')
