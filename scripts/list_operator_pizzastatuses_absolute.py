import json
import os

# Always use absolute path relative to this script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, '..', 'data', 'pay_PizzaStatuses.json')

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    pizza_statuses = json.load(f)

operator_statuses = [p for p in pizza_statuses if p.get('IsOperator') is True]

output_lines = []
output_lines.append('Operator PizzaStatuses (including duplicates):')
for p in operator_statuses:
    output_lines.append(f"ID: {p['ID']}")
    output_lines.append(f"Status: {p['Status']}")
    output_lines.append(f"Description: {p.get('Description', '')}")
    output_lines.append(f"MobileAppOrder: {p.get('MobileAppOrder', '')}")
    output_lines.append(f"ClientID: {p.get('ClientID', '')}")
    output_lines.append(f"isActive: {p.get('isActive', '')}")
    output_lines.append(f"__IMTINDEX__: {p.get('__IMTINDEX__', '')}")
    output_lines.append(f"__IMTLENGTH__: {p.get('__IMTLENGTH__', '')}")
    output_lines.append('-' * 40)

output_text = '\n'.join(output_lines)
print(output_text)

# Write to txt file in the same directory as the script
output_path = os.path.join(SCRIPT_DIR, 'operator_pizzastatuses.txt')
with open(output_path, 'w', encoding='utf-8') as out_f:
    out_f.write(output_text)
