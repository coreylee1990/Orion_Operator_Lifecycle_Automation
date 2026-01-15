import json

with open('data/pay_PizzaStatuses.json', 'r', encoding='utf-8') as f:
    statuses = json.load(f)

operator_statuses = [
    {
        'ID': s['ID'],
        'Status': s['Status'].strip(),
        'Description': s.get('Description', '').strip()
    }
    for s in statuses if s.get('IsOperator') is True
]

print('Operator PizzaStatuses:')
for s in operator_statuses:
    print(f"- {s['Status']} (ID: {s['ID']}) | {s['Description']}")

if not operator_statuses:
    print('No operator statuses found.')
