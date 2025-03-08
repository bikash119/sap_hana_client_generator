#!/usr/bin/env python
"""Example script demonstrating how to use the SAP HANA Client Generator.

This script shows how to generate a client library from an OpenAPI specification
and then use the generated client to make API calls.
"""

import os
import sys
from sap_hana_client_generator import generate_client_from_spec

def main():
    """Generate a client library from the SAP HANA OpenAPI specification."""
    # Get the path to the OpenAPI specification
    spec_path = os.path.join('..', 'sap_python_lib', 'API_SALES_ORDER_SRV.yaml')
    
    if not os.path.exists(spec_path):
        print(f"Error: OpenAPI specification not found at {spec_path}")
        return 1
    
    # Generate the client library
    print(f"Generating client library from {spec_path}...")
    output_dir = generate_client_from_spec(spec_path)
    
    print(f"\nClient library generated successfully at: {output_dir}")
    print("\nYou can now use the generated client as follows:")
    print("\n```python")
    print(f"from {os.path.basename(output_dir)} import Client")
    print("")
    print("# Initialize the client")
    print("client = Client(")
    print('    base_url="https://your-sap-instance.com/sap/opu/odata/sap/API_SALES_ORDER_SRV",')
    print('    username="your-username",')
    print('    password="your-password"')
    print(")")
    print("")
    print("# Example: Get a list of sales orders")
    print("# response = client.sales_order.get_sales_orders()")
    print("# print(response)")
    print("```")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 