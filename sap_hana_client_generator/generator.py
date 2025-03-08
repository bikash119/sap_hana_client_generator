"""Client generator for SAP HANA API.

This module provides functionality to generate a Python client library from an OpenAPI specification.
"""

import os
import re
import json
import yaml
import shutil
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class ClientGenerator:
    """Generator for creating Python client libraries from OpenAPI specifications.
    
    This class handles the parsing of OpenAPI specifications and generation of
    Python client code including models, API endpoints, and package structure.
    """

    def __init__(self, spec_path: str, output_dir: str = None):
        """Initialize the client generator.
        
        Args:
            spec_path: Path to the OpenAPI specification file (JSON or YAML)
            output_dir: Directory where the generated client will be saved.
                If None, a directory will be created based on the API title.
        """
        self.spec_path = spec_path
        self.spec = self._load_spec(spec_path)
        
        api_title = self.spec.get('info', {}).get('title', 'sap_api')
        package_name = self._sanitize_name(api_title).lower().replace('-', '_')
        
        self.package_name = package_name
        self.output_dir = output_dir or os.path.join(os.getcwd(), package_name)
        self.package_dir = os.path.join(self.output_dir, package_name)

    def _load_spec(self, spec_path: str) -> Dict[str, Any]:
        """Load and parse the OpenAPI specification.
        
        Args:
            spec_path: Path to the OpenAPI specification file
            
        Returns:
            The parsed OpenAPI specification as a dictionary
            
        Raises:
            ValueError: If the file format is not supported or the file cannot be parsed
        """
        if not os.path.exists(spec_path):
            raise ValueError(f"Specification file not found: {spec_path}")
            
        with open(spec_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if spec_path.endswith('.json'):
            return json.loads(content)
        elif spec_path.endswith('.yaml') or spec_path.endswith('.yml'):
            return yaml.safe_load(content)
        else:
            raise ValueError(f"Unsupported specification format: {spec_path}")

    def _sanitize_name(self, name: str) -> str:
        """Convert a name to a valid Python identifier.
        
        Args:
            name: The name to sanitize
            
        Returns:
            A valid Python identifier derived from the input name
        """
        # Replace non-alphanumeric characters with underscores
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        
        # Ensure the name starts with a letter or underscore
        if name and not name[0].isalpha() and name[0] != '_':
            name = 'api_' + name
            
        return name

    def _get_python_type(self, schema: Dict[str, Any]) -> str:
        """Convert OpenAPI schema type to Python type annotation.
        
        Args:
            schema: OpenAPI schema object
            
        Returns:
            Python type annotation as a string
        """
        if not schema:
            return 'Any'
            
        schema_type = schema.get('type')
        schema_format = schema.get('format')
        
        if schema_type == 'integer':
            return 'int'
        elif schema_type == 'number':
            return 'float'
        elif schema_type == 'boolean':
            return 'bool'
        elif schema_type == 'string':
            if schema_format == 'date-time':
                return 'datetime'
            elif schema_format == 'date':
                return 'date'
            elif schema_format == 'binary':
                return 'bytes'
            return 'str'
        elif schema_type == 'array':
            items = schema.get('items', {})
            item_type = self._get_python_type(items)
            return f'List[{item_type}]'
        elif schema_type == 'object' or 'properties' in schema:
            return 'Dict[str, Any]'
        elif '$ref' in schema:
            ref = schema['$ref']
            model_name = ref.split('/')[-1]
            return model_name
        
        return 'Any'

    def generate(self) -> str:
        """Generate the client library.
        
        This method orchestrates the entire generation process, creating
        the package structure, models, API modules, and documentation.
        
        Returns:
            The path to the generated client library
        """
        logger.info(f"Generating client library for {self.spec.get('info', {}).get('title', 'API')}")
        
        # Create the package structure
        self._create_package_structure()
        
        # Generate the client module
        self._generate_client_module()
        
        # Generate models
        self._generate_models()
        
        # Generate API modules
        self._generate_api_modules()
        
        # Generate setup.py
        self._generate_setup_py()
        
        # Generate README
        self._generate_readme()
        
        logger.info(f"Client library generated at {self.output_dir}")
        return self.output_dir

    def _create_package_structure(self) -> None:
        """Create the package directory structure.
        
        This method creates the necessary directories and files for a Python package.
        """
        # Create main package directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create package subdirectory
        os.makedirs(self.package_dir, exist_ok=True)
        
        # Create models directory
        os.makedirs(os.path.join(self.package_dir, 'models'), exist_ok=True)
        
        # Create api directory
        os.makedirs(os.path.join(self.package_dir, 'api'), exist_ok=True)
        
        # Create __init__.py files
        with open(os.path.join(self.package_dir, '__init__.py'), 'w', encoding='utf-8') as f:
            f.write(f'''"""Client library for {self.spec.get('info', {}).get('title', 'SAP API')}.

This package was generated from an OpenAPI specification.
"""

from .client import Client

__version__ = '0.1.0'
''')
        
        with open(os.path.join(self.package_dir, 'models', '__init__.py'), 'w', encoding='utf-8') as f:
            f.write('"""Generated model classes."""\n\n')
            
        with open(os.path.join(self.package_dir, 'api', '__init__.py'), 'w', encoding='utf-8') as f:
            f.write('"""Generated API endpoint modules."""\n\n')

    def _generate_client_module(self) -> None:
        """Generate the main client module.
        
        This method creates the main Client class that serves as the entry point
        for the generated library.
        """
        package_dir = self.package_dir
        
        with open(os.path.join(package_dir, 'client.py'), 'w', encoding='utf-8') as f:
            f.write(f"""\"\"\"Client for {self.spec.get('info', {}).get('title', 'SAP API')}.

This module provides the main client class for interacting with the API.
\"\"\"

import logging
import requests
from typing import Dict, Any, Optional, Union, List
from urllib.parse import urljoin

# Import API modules
""")

            # Import API modules
            paths = self.spec.get('paths', {})
            api_modules = set()
            
            for path, path_item in paths.items():
                for method in ['get', 'post', 'put', 'delete', 'patch']:
                    if method in path_item:
                        operation = path_item[method]
                        tag = operation.get('tags', ['default'])[0]
                        module_name = self._sanitize_name(tag).lower()
                        class_name = self._sanitize_name(tag).capitalize() + 'Api'
                        api_modules.add((module_name, class_name))
            
            for module_name, class_name in sorted(api_modules):
                f.write(f"from .api.{module_name} import {class_name}\n")
            
            f.write("""
logger = logging.getLogger(__name__)

class Client:
    \"\"\"Client for interacting with the API.
    
    This class provides access to all API endpoints through dedicated API objects.
    \"\"\"
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, 
                 username: Optional[str] = None, password: Optional[str] = None,
                 timeout: int = 60, verify: bool = True):
        \"\"\"Initialize the API client.
        
        Args:
            base_url: The base URL of the API
            api_key: Optional API key for authentication
            username: Optional username for basic authentication
            password: Optional password for basic authentication
            timeout: Request timeout in seconds
            verify: Whether to verify SSL certificates
        \"\"\"
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.username = username
        self.password = password
        self.timeout = timeout
        self.verify = verify
        self.session = requests.Session()
        
        # Initialize API objects
""")
            
            # Initialize API objects
            for module_name, class_name in sorted(api_modules):
                f.write(f"        self.{module_name} = {class_name}(self)\n")
            
            f.write("""
    def request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None,
                data: Optional[Any] = None, json: Optional[Any] = None,
                headers: Optional[Dict[str, str]] = None) -> requests.Response:
        \"\"\"Make a request to the API.
        
        Args:
            method: HTTP method (get, post, put, delete, patch)
            path: API endpoint path
            params: Query parameters
            data: Request body for form data
            json: Request body for JSON data
            headers: Additional headers
            
        Returns:
            Response object
        \"\"\"
        url = urljoin(self.base_url, path)
        request_headers = headers or {}
        
        logger.debug(f"Making {method} request to {url}")
        
        # Add authentication
        if self.api_key:
            request_headers['Authorization'] = f"Bearer {self.api_key}"
        
        auth = None
        if self.username and self.password:
            auth = (self.username, self.password)
        
        response = self.session.request(
            method=method,
            url=url,
            params=params,
            data=data,
            json=json,
            headers=request_headers,
            auth=auth,
            timeout=self.timeout,
            verify=self.verify
        )
        
        logger.debug(f"Response status: {response.status_code}")
        
        # Raise exception for error responses
        response.raise_for_status()
        
        return response
""")

    def _generate_models(self) -> None:
        """Generate model classes from schema definitions.
        
        This method creates Python classes for each schema defined in the OpenAPI spec.
        """
        models_dir = os.path.join(self.package_dir, 'models')
        
        # Get all schema definitions
        schemas = self.spec.get('components', {}).get('schemas', {})
        
        # Update models/__init__.py to import all models
        with open(os.path.join(models_dir, '__init__.py'), 'w', encoding='utf-8') as f:
            f.write('"""Generated model classes."""\n\n')
            
            for schema_name in schemas:
                model_name = self._sanitize_name(schema_name)
                f.write(f"from .{model_name.lower()} import {model_name}\n")
        
        # Generate a file for each model
        for schema_name, schema in schemas.items():
            model_name = self._sanitize_name(schema_name)
            file_path = os.path.join(models_dir, f"{model_name.lower()}.py")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"""\"\"\"Model definition for {schema_name}.\"\"\"

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime, date

@dataclass
class {model_name}:
    \"\"\"Model class for {schema_name}.
    
    This class was generated from the OpenAPI schema.
    \"\"\"
""")
                
                # Add properties
                properties = schema.get('properties', {})
                required = schema.get('required', [])
                
                for prop_name, prop_schema in properties.items():
                    python_name = self._sanitize_name(prop_name)
                    python_type = self._get_python_type(prop_schema)
                    
                    if prop_name in required:
                        f.write(f"    {python_name}: {python_type}\n")
                    else:
                        f.write(f"    {python_name}: Optional[{python_type}] = None\n")
                
                # If no properties, add a pass statement
                if not properties:
                    f.write("    pass\n")

    def _generate_api_modules(self) -> None:
        """Generate API endpoint modules.
        
        This method creates Python modules for each API tag in the OpenAPI spec.
        """
        api_dir = os.path.join(self.package_dir, 'api')
        
        # Group operations by tag
        tags_operations = {}
        paths = self.spec.get('paths', {})
        
        for path, path_item in paths.items():
            for method in ['get', 'post', 'put', 'delete', 'patch']:
                if method in path_item:
                    operation = path_item[method]
                    tags = operation.get('tags', ['default'])
                    
                    for tag in tags:
                        if tag not in tags_operations:
                            tags_operations[tag] = []
                        
                        tags_operations[tag].append({
                            'path': path,
                            'method': method,
                            'operation': operation,
                            'operation_id': operation.get('operationId')
                        })
        
        # Generate a file for each tag
        for tag, operations in tags_operations.items():
            module_name = self._sanitize_name(tag).lower()
            class_name = self._sanitize_name(tag).capitalize() + 'Api'
            file_path = os.path.join(api_dir, f"{module_name}.py")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"""\"\"\"API endpoints for {tag}.\"\"\"

from typing import Dict, List, Any, Optional, Union
import json
from ..models import *

class {class_name}:
    \"\"\"API endpoints for {tag}.\"\"\"
    
    def __init__(self, client):
        \"\"\"Initialize the API.
        
        Args:
            client: The API client instance
        \"\"\"
        self.client = client
""")
                
                # Generate methods for each operation
                for op in operations:
                    if not op.get('operation_id'):
                        continue
                        
                    operation_id = self._sanitize_name(op['operation_id'])
                    path = op['path']
                    method = op['method']
                    operation = op['operation']
                    
                    # Get parameters
                    parameters = operation.get('parameters', [])
                    path_params = [p for p in parameters if p.get('in') == 'path']
                    query_params = [p for p in parameters if p.get('in') == 'query']
                    header_params = [p for p in parameters if p.get('in') == 'header']
                    
                    # Get request body
                    request_body = operation.get('requestBody', {})
                    request_content = request_body.get('content', {})
                    
                    # Get response
                    responses = operation.get('responses', {})
                    success_response = responses.get('200', {}) or responses.get('201', {})
                    response_content = success_response.get('content', {})
                    
                    # Determine return type
                    return_type = 'Any'
                    if 'application/json' in response_content:
                        schema = response_content['application/json'].get('schema', {})
                        return_type = self._get_python_type(schema)
                    
                    # Generate method signature
                    f.write(f"\n    def {operation_id}(self")
                    
                    # Add path parameters
                    for param in path_params:
                        param_name = self._sanitize_name(param['name'])
                        param_type = self._get_python_type(param.get('schema', {}))
                        f.write(f", {param_name}: {param_type}")
                    
                    # Add query parameters
                    for param in query_params:
                        param_name = self._sanitize_name(param['name'])
                        param_type = self._get_python_type(param.get('schema', {}))
                        required = param.get('required', False)
                        
                        if required:
                            f.write(f", {param_name}: {param_type}")
                        else:
                            f.write(f", {param_name}: Optional[{param_type}] = None")
                    
                    # Add request body
                    if request_content:
                        if 'application/json' in request_content:
                            schema = request_content['application/json'].get('schema', {})
                            body_type = self._get_python_type(schema)
                            required = request_body.get('required', False)
                            
                            if required:
                                f.write(f", data: {body_type}")
                            else:
                                f.write(f", data: Optional[{body_type}] = None")
                    
                    # Add header parameters
                    for param in header_params:
                        param_name = self._sanitize_name(param['name'])
                        required = param.get('required', False)
                        
                        if required:
                            f.write(f", {param_name}: str")
                        else:
                            f.write(f", {param_name}: Optional[str] = None")
                    
                    # Close method signature and add return type
                    f.write(f") -> {return_type}:\n")
                    
                    # Add docstring
                    f.write(f"        \"\"\"")
                    if operation.get('summary'):
                        f.write(f"{operation['summary']}\n        \n")
                    if operation.get('description'):
                        f.write(f"{operation['description']}\n        \n")
                    
                    f.write("        Args:\n")
                    for param in path_params + query_params:
                        param_name = self._sanitize_name(param['name'])
                        param_desc = param.get('description', 'No description')
                        f.write(f"            {param_name}: {param_desc}\n")
                    
                    if request_content and 'application/json' in request_content:
                        f.write("            data: Request body\n")
                    
                    for param in header_params:
                        param_name = self._sanitize_name(param['name'])
                        param_desc = param.get('description', 'No description')
                        f.write(f"            {param_name}: {param_desc}\n")
                    
                    f.write("        \n")
                    f.write("        Returns:\n")
                    f.write(f"            {return_type}: Response data\n")
                    f.write("        \"\"\"\n")
                    
                    # Method implementation
                    # Format the path with parameters
                    if path_params:
                        path_format_args = ", ".join([f"{p['name']}={self._sanitize_name(p['name'])}" for p in path_params])
                        f.write(f"        path = f\"{path}\".format({path_format_args})\n")
                    else:
                        f.write(f"        path = \"{path}\"\n")
                    
                    # Add query parameters
                    if query_params:
                        f.write("        params = {}\n")
                        for param in query_params:
                            param_name = self._sanitize_name(param['name'])
                            f.write(f"        if {param_name} is not None:\n")
                            f.write(f"            params['{param['name']}'] = {param_name}\n")
                    else:
                        f.write("        params = None\n")
                    
                    # Add headers
                    if header_params:
                        f.write("        headers = {}\n")
                        for param in header_params:
                            param_name = self._sanitize_name(param['name'])
                            f.write(f"        if {param_name} is not None:\n")
                            f.write(f"            headers['{param['name']}'] = {param_name}\n")
                    else:
                        f.write("        headers = None\n")
                    
                    # Make the request
                    if request_content and 'application/json' in request_content:
                        f.write(f"        response = self.client.request('{method}', path, params=params, json=data, headers=headers)\n")
                    else:
                        f.write(f"        response = self.client.request('{method}', path, params=params, headers=headers)\n")
                    
                    # Process the response
                    if 'application/json' in response_content:
                        f.write("        return response.json()\n")
                    else:
                        f.write("        return response.text\n")

    def _generate_setup_py(self) -> None:
        """Generate setup.py file for the package.
        
        This method creates a setup.py file with package metadata.
        """
        api_info = self.spec.get('info', {})
        api_title = api_info.get('title', 'SAP API')
        api_description = api_info.get('description', 'Python client for SAP API')
        api_version = api_info.get('version', '0.1.0')
        
        with open(os.path.join(self.output_dir, 'setup.py'), 'w', encoding='utf-8') as f:
            f.write(f"""from setuptools import setup, find_packages

setup(
    name="{self.package_name}",
    version="{api_version}",
    description="{api_title} Python Client",
    long_description=\"\"\"
{api_description}
\"\"\",
    author="SAP HANA Client Generator",
    author_email="user@example.com",
    url="https://github.com/example/sap-hana-client",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "pyyaml>=5.4.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
)
""")

    def _generate_readme(self) -> None:
        """Generate README.md file for the package.
        
        This method creates a README.md file with usage instructions.
        """
        api_info = self.spec.get('info', {})
        api_title = api_info.get('title', 'SAP API')
        api_description = api_info.get('description', 'Python client for SAP API')
        
        with open(os.path.join(self.output_dir, 'README.md'), 'w', encoding='utf-8') as f:
            f.write(f"""# {api_title} Python Client

This package provides a Python client for the {api_title}.

## Description

{api_description}

## Installation

```bash
pip install {self.package_name}
```

Or install from source:

```bash
git clone https://github.com/example/{self.package_name}.git
cd {self.package_name}
pip install -e .
```

## Usage

```python
from {self.package_name} import Client

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

## API Documentation

This client was generated from an OpenAPI specification. For detailed API documentation, please refer to the original API documentation.

## License

MIT
""")


def generate_client_from_spec(spec_path: str, output_dir: Optional[str] = None) -> str:
    """Generate a Python client library from an OpenAPI specification.
    
    Args:
        spec_path: Path to the OpenAPI specification file (JSON or YAML)
        output_dir: Directory where the generated client will be saved.
            If None, a directory will be created based on the API title.
            
    Returns:
        The path to the generated client library
    """
    generator = ClientGenerator(spec_path, output_dir)
    return generator.generate() 