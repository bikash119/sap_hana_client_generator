# SAP HANA Client Generator

A Python package that generates client libraries from OpenAPI specifications for SAP HANA APIs.

## Description

This package provides a command-line tool and Python API for generating client libraries from OpenAPI specifications. The generated clients provide a convenient way to interact with SAP HANA APIs.

## Installation

```bash
pip install sap-hana-client-generator
```

Or install from source:

```bash
git clone https://github.com/example/sap-hana-client-generator.git
cd sap-hana-client-generator
pip install -e .
```

## Usage

### Command-line Interface

```bash
# Generate a client library from an OpenAPI specification
sap-hana-client-generator path/to/openapi.yaml --output-dir my_client

# Show help
sap-hana-client-generator --help
```

### Python API

```python
from sap_hana_client_generator import generate_client_from_spec

# Generate a client library from an OpenAPI specification
output_dir = generate_client_from_spec('path/to/openapi.yaml', 'my_client')
print(f"Client library generated at: {output_dir}")
```

## Generated Client Usage

The generated client library can be used as follows:

```python
from my_client import Client

# Initialize the client
client = Client(
    base_url="https://api.example.com",
    api_key="your-api-key",  # Optional
    username="your-username",  # Optional
    password="your-password",  # Optional
)

# Use the client to make API calls
# Example:
# response = client.some_api.some_operation(param1="value1", param2="value2")
# print(response)
```

## Features

- Generates a complete Python package from an OpenAPI specification
- Supports authentication methods: API key, Basic Auth
- Generates model classes for request and response data
- Organizes API endpoints by tags
- Includes proper documentation and type hints

## License

MIT 