
import os
import sys

# Ensure we can import from local scripts folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from operator_lifecycle import OperatorLifecycleManager, ProcessAuditor

# Output directory config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "generated", "generate_artifacts")

def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    return OUTPUT_DIR

def generate_artifacts():
    out_dir = ensure_output_dir()
    manager = OperatorLifecycleManager()
    
    # 0. Generate Detailed Process Audit
    print("Running Process Audit...")
    auditor = ProcessAuditor(manager.status_types)
    audit_text = auditor.generate_audit_text()
    
    audit_path = os.path.join(out_dir, "process_gap_analysis.txt")
    with open(audit_path, "w") as f:
        f.write(audit_text)
    print(f"Generated {audit_path}")

    # 1.5 Generate Division Tables
    print("Generating Division Tables...")
    tables_text = auditor.generate_division_tables()
    table_path = os.path.join(out_dir, "division_process_tables.md")
    with open(table_path, "w") as f:
        f.write(tables_text)
    print(f"Generated {table_path}")

    flow_data = manager.get_ordered_flow_data()
    
    # 1. Generate Text Report
    report_path = os.path.join(out_dir, "requirements_report.txt")
    with open(report_path, "w") as f:
        f.write("Orion Operator Lifecycle - Requirements Matrix\n")
        f.write("==============================================\n\n")
        
        for item in flow_data:
            reqs = ", ".join(item['requirements']) if item['requirements'] else "No specific certs"
            f.write(f"Step {item['order']}: {item['name']}\n")
            f.write(f"  -> Required to Enter: {reqs}\n\n")
            
    print(f"Generated {report_path}")

    # 2. Generate Mermaid Flowchart
    mermaid_path = os.path.join(out_dir, "lifecycle_flowchart.md")
    with open(mermaid_path, "w") as f:
        f.write("# Operator Lifecycle Flowchart\n\n")
        f.write("```mermaid\n")
        f.write("graph TD\n")
        
        # Create Nodes and Edges
        # We assume a linear progression 1 -> 2 -> ...
        
        for i in range(len(flow_data) - 1):
            curr = flow_data[i]
            next_step = flow_data[i+1]
            
            # Node definitions
            # clean names for IDs
            cid = f"S{curr['order']}"
            nid = f"S{next_step['order']}"
            
            c_label = f"{curr['order']}. {curr['name']}"
            n_label = f"{next_step['order']}. {next_step['name']}"
            
            # Requirements are the "gate" to the next step
            # Actually, per logic, the requirements for S(n) are needed to enter S(n).
            # So the edge S(n-1) -> S(n) should be labeled with S(n)'s requirements.
            
            gate_reqs = next_step['requirements']
            edge_label = "<br/>".join(gate_reqs) if gate_reqs else "Auto/None"
            
            # Using Mermaid syntax
            # S1[1. REGISTRATION] -->|Requirements| S2[2. ONBOARDING]
            
            if i == 0:
                # write first node explicit
                f.write(f"    {cid}[\"{c_label}\"]\n")

            f.write(f"    {cid} -->|{edge_label}| {nid}[\"{n_label}\"]\n")
            
        f.write("```\n")
        
    print(f"Generated {mermaid_path}")

    # 3. Generate Python Flowchart Script (using 'graphviz' library if user installs it)
    # This fulfills the request for a "python flowchart" - a script they can run later if they setup environment
    py_chart_path = os.path.join(out_dir, "render_flowchart.py")
    with open(py_chart_path, "w") as f:
        # Create a self-contained script content
        script_content = f"""
try:
    from graphviz import Digraph
except ImportError:
    print("Error: 'graphviz' library not found. Please install it via 'pip install graphviz' and ensure Graphviz is installed on your system.")
    exit(1)

dot = Digraph(comment='Orion Operator Lifecycle')
dot.attr(rankdir='TB')

data = {repr(flow_data)}

# Add nodes
for step in data:
    label = f"{{step['order']}}. {{step['name']}}"
    dot.node(str(step['order']), label, shape='box', style='rounded')

# Add edges
for i in range(len(data) - 1):
    curr = data[i]
    nxt = data[i+1]
    
    reqs = "\\n".join(nxt['requirements'])
    label = reqs if reqs else " "
    
    dot.edge(str(curr['order']), str(nxt['order']), label=label)

output_filename = 'lifecycle_flowchart_graph'
dot.render(output_filename, view=False, format='png')
print(f"Rendered flowchart to {{output_filename}}.png")
"""
        f.write(script_content)
    
    print(f"Generated {py_chart_path} (Requires 'graphviz' library to run)")

if __name__ == "__main__":
    generate_artifacts()
