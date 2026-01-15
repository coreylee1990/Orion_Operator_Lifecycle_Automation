
import json
import os

# Configurable paths
status_types_path = r'C:\Users\PC\Desktop\Projects\Orion_Operator_Lifecycle_Automation-master\data\pay_StatusTypes.json'
pizza_statuses_path = r'C:\Users\PC\Desktop\Projects\Orion_Operator_Lifecycle_Automation-master\data\pay_PizzaStatuses.json'
output_dir = r'C:\Users\PC\Desktop\Projects\Orion_Operator_Lifecycle_Automation-master\output'

# DivisionID for 3 - TX
DIVISION_ID = '3 - TX'

# Load status types
with open(status_types_path, 'r', encoding='utf-8') as f:
    status_types = json.load(f)

# Load pizza statuses (for IsOperator lookup)
with open(pizza_statuses_path, 'r', encoding='utf-8') as f:
    pizza_statuses = json.load(f)
pizza_status_map = {p["ID"]: p for p in pizza_statuses if p.get("ID")}

# Find all StatusTypes for division 3 - TX that:
# - DivisionID matches
# - not deleted (isDeleted/IsDelete not true/1/'1')
# - PizzaStatusID exists and is in pizza_statuses
# - isActive is '1' or True (or missing means active)
# - IsOperator is true in the linked PizzaStatus
results = []
for st in status_types:
    if (
        st.get('DivisionID') == DIVISION_ID
        and not (st.get('isDeleted') is True or st.get('IsDelete') is True or str(st.get('isDeleted', '')).strip() == '1' or str(st.get('IsDelete', '')).strip() == '1' or str(st.get('isDeleted', '')).strip().lower() == 'true' or str(st.get('IsDelete', '')).strip().lower() == 'true')
        and st.get('PizzaStatusID')
        and st.get('PizzaStatusID') in pizza_status_map
        and (str(st.get('isActive', '1')).strip() == '1' or st.get('isActive') is True)
        and (pizza_status_map[st['PizzaStatusID']].get('IsOperator') is True)
    ):
        results.append({
            'ID': st.get('Id') or st.get('ID'),
            'Status': st.get('Status', ''),
            'PizzaStatusID': st.get('PizzaStatusID'),
            'Description': st.get('Description', ''),
        })


# Sort results by OrderID (as integer, fallback to 9999 if missing)
def get_order(st):
    try:
        return int(st.get('OrderID', 9999))
    except Exception:
        return 9999
for i, st in enumerate(status_types):
    if 'OrderID' in st and st['OrderID'] is not None:
        try:
            st['OrderID'] = int(st['OrderID'])
        except Exception:
            pass
results.sort(key=lambda st: st.get('OrderID', 9999))

output_lines = []
output_lines.append(f"StatusTypes for Division {DIVISION_ID} (IsOperator only, not deleted, with PizzaStatusID): {len(results)} found\n")
for s in results:
    output_lines.append(f"- {s['Status']} (ID: {s['ID']}) | PizzaStatusID: {s['PizzaStatusID']} | {s['Description']}")

# Print to console
for line in output_lines:
    print(line)

# Write to output file
os.makedirs(output_dir, exist_ok=True)
div_id_clean = DIVISION_ID.replace(' ', '').replace('-', '')
output_path = os.path.join(output_dir, f'statuses_{div_id_clean}.txt')
with open(output_path, 'w', encoding='utf-8') as f:
    for line in output_lines:
        f.write(line + '\n')
