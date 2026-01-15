

import json
import os
import sys

cert_types_path = r'C:\Users\PC\Desktop\Projects\Orion_Operator_Lifecycle_Automation-master\data\pay_CertTypes.json'
output_folder = r'C:\Users\PC\Desktop\Projects\Orion_Operator_Lifecycle_Automation-master\output'

def main():
    # Accept command-line arguments
    pizza_status_id = None
    division_id = None
    if len(sys.argv) > 1:
        pizza_status_id = sys.argv[1].strip()
    if len(sys.argv) > 2:
        division_id = sys.argv[2].strip()

    # Prompt only if not provided
    if not pizza_status_id:
        pizza_status_id = input("Enter PizzaStatusID to filter by: ").strip()
    if division_id is None:
        division_id = input("Enter DivisionID to filter by (optional, e.g. '10 - OR'): ").strip()

    with open(cert_types_path, 'r', encoding='utf-8') as f:
        cert_types = json.load(f)

    results = []
    for cert in cert_types:
        if cert.get('PizzaStatusID') == pizza_status_id:
            if division_id:
                if str(cert.get('DivisionID', '')).strip() == division_id:
                    results.append(cert)
            else:
                results.append(cert)

    output_lines = [
        f"Certifications with PizzaStatusID {pizza_status_id}" + (f" and DivisionID {division_id}" if division_id else "") + ":\n"
    ]
    for cert in results:
        output_lines.append(f"- Certification: {cert.get('Certification', 'UNKNOWN')}\n  Description: {cert.get('Description', 'UNKNOWN')}\n  DivisionID: {cert.get('DivisionID', 'UNKNOWN')}\n")

    print(''.join(output_lines))

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    filename = f"certs_{pizza_status_id}" + (f"_Div{division_id.replace(' ', '').replace('-', '')}" if division_id else "") + ".txt"
    output_path = os.path.join(output_folder, filename)
    with open(output_path, 'w', encoding='utf-8') as out_f:
        out_f.write(''.join(output_lines))
    print(f"Results saved to {output_path}")

if __name__ == '__main__':
    main()
