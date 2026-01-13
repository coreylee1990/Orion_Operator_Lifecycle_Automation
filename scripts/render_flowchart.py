
try:
    from graphviz import Digraph
except ImportError:
    print("Error: 'graphviz' library not found. Please install it via 'pip install graphviz' and ensure Graphviz is installed on your system.")
    exit(1)

dot = Digraph(comment='Orion Operator Lifecycle')
dot.attr(rankdir='TB')

data = [{'order': 1, 'name': 'REGISTRATION', 'requirements': ["Driver's License"]}, {'order': 2, 'name': 'ONBOARDING', 'requirements': ['Background Check']}, {'order': 3, 'name': 'CREDENTIALING', 'requirements': ['Drug Test Results']}, {'order': 4, 'name': 'DOT SCREENING', 'requirements': ['Medical Card', 'Motor Vehicle Record']}, {'order': 5, 'name': 'ORIENTATION-BIG STAR SAFETY & SERVICE', 'requirements': ['Safety Orientation Cert']}, {'order': 6, 'name': 'ORIENTATION-CLIENT HOSTED', 'requirements': []}, {'order': 7, 'name': 'Approved for CHO (Client Hosted)', 'requirements': []}, {'order': 8, 'name': 'APPROVED-ORIENTATION BTW', 'requirements': []}, {'order': 9, 'name': 'COMPLIANCE REVIEW', 'requirements': []}, {'order': 10, 'name': 'SBPC APPROVED FOR SERVICE', 'requirements': []}, {'order': 11, 'name': 'Approved for Service', 'requirements': []}, {'order': 12, 'name': 'APPROVED FOR CONTRACTING', 'requirements': ['Signed Contract']}, {'order': 13, 'name': 'APPROVED FOR LEASING', 'requirements': ['Vehicle Lease Agreement']}, {'order': 14, 'name': 'IN-SERVICE', 'requirements': []}]

# Add nodes
for step in data:
    label = f"{step['order']}. {step['name']}"
    dot.node(str(step['order']), label, shape='box', style='rounded')

# Add edges
for i in range(len(data) - 1):
    curr = data[i]
    nxt = data[i+1]
    
    reqs = "\n".join(nxt['requirements'])
    label = reqs if reqs else " "
    
    dot.edge(str(curr['order']), str(nxt['order']), label=label)

output_filename = 'lifecycle_flowchart_graph'
dot.render(output_filename, view=False, format='png')
print(f"Rendered flowchart to {output_filename}.png")
