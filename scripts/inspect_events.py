
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def analyze_events():
    st_path = os.path.join(DATA_DIR, 'pay_StatusTypes.txt')
    try:
        with open(st_path, 'r') as f:
            statuses = json.load(f)
            
        print(f"Total Statuses: {len(statuses)}")
        
        keywords = ['accident', 'event', 'incident']
        
        matches = []
        for st in statuses:
            name = st.get('Status')
            desc = st.get('Description')
            
            name = name.lower() if name else ""
            desc = desc.lower() if desc else ""
            
            if any(k in name for k in keywords) or any(k in desc for k in keywords):
                matches.append(st)
                
        print(f"Found {len(matches)} statuses matching keywords: {keywords}")
        
        # Analyze common properties
        fleet_true = 0
        fleet_false = 0
        prov_true = 0
        prov_false = 0
        oos_true = 0
        oos_false = 0
        
        samples = matches[:5]
        
        for m in matches:
            if m.get('Fleet') is True: fleet_true += 1
            else: fleet_false += 1
            
            if m.get('Providers') is True: prov_true += 1
            else: prov_false += 1
            
            if m.get('OutOfServiceFlag') is True: oos_true += 1
            else: oos_false += 1

        print("\n--- Stats for Keywords Matches ---")
        print(f"Fleet=True: {fleet_true}, Fleet=False: {fleet_false}")
        print(f"Providers=True: {prov_true}, Providers=False: {prov_false}")
        print(f"OutOfServiceFlag=True: {oos_true}, OutOfServiceFlag=False: {oos_false}")
        
        print("\n--- Sample Matches ---")
        for s in samples:
            print(f"Status: {s.get('Status')}") 
            print(f"  Fleet: {s.get('Fleet')}")
            print(f"  Providers: {s.get('Providers')}")
            print(f"  OutOfService: {s.get('OutOfServiceFlag')}")
            print(f"  PizzaStatusID: {s.get('PizzaStatusID')}")
            print("-" * 20)

        # Check unique PizzaStatusIDs
        pids = set(m.get('PizzaStatusID') for m in matches)
        print(f"\nUnique PizzaStatusIDs in matches: {pids}")
        
        print("\n--- Non-Fleet Keyword Matches ---")
        for m in matches:
            if m.get('Fleet') is False:
                print(f"Status: {m.get('Status')} | Fleet: {m.get('Fleet')} | PizzaStatusID: {m.get('PizzaStatusID')}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_events()
