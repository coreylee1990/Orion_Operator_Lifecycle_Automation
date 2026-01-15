
from operator_lifecycle import OperatorLifecycleManager

def run_tests():
    print("Initializing Manager...")
    manager = OperatorLifecycleManager()
    
    # Test 1: Pick an operator and see details
    print("\n--- Test 1: Inspect Operator 'Demarius' ---")
    op = manager.get_operator("Demarius")
    if op:
        print(f"Found: {op.get('FirstName')} {op.get('LastName')}")
        
        # Check Completed
        print("Completed Certs:")
        completed = manager.get_operator_completed_certs(op.get('Id'))
        for c in completed:
            print(f" - {c['Name']} ({c['Status']})")
            
        # Check Next Status
        next_info = manager.get_next_status_requirements(op)
        print(f"Targeting Status: {next_info['NextStatusName']}")
        print(f"Required Certs: {next_info['RequiredCerts']}")
    else:
        print("Demarius not found.")

    # Test 2: Generate Report
    print("\n--- Test 2: Requirements Structure Report ---")
    report = manager.generate_report()
    # Print first 5 steps
    for i, (step, reqs) in enumerate(report.items()):
        if i >= 5: break
        print(f"{step}: {reqs}")

if __name__ == "__main__":
    run_tests()
