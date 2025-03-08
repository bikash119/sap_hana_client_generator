"""Tests for the generator module."""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from sap_hana_client_generator.generator import ClientGenerator, generate_client_from_spec


class TestClientGenerator(unittest.TestCase):
    """Test cases for the ClientGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a minimal OpenAPI spec for testing
        self.test_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0",
                "description": "API for testing"
            },
            "paths": {
                "/test": {
                    "get": {
                        "operationId": "getTest",
                        "tags": ["test"],
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "string"},
                                                "name": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "TestModel": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "value": {"type": "integer"}
                        },
                        "required": ["id", "name"]
                    }
                }
            }
        }

    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('sap_hana_client_generator.generator.ClientGenerator._load_spec')
    def test_init(self, mock_load_spec):
        """Test initialization of ClientGenerator."""
        mock_load_spec.return_value = self.test_spec
        
        generator = ClientGenerator("dummy_path.yaml", self.temp_dir)
        
        self.assertEqual(generator.spec_path, "dummy_path.yaml")
        self.assertEqual(generator.spec, self.test_spec)
        self.assertEqual(generator.package_name, "test_api")
        self.assertEqual(generator.output_dir, self.temp_dir)
        self.assertEqual(generator.package_dir, os.path.join(self.temp_dir, "test_api"))

    @patch('sap_hana_client_generator.generator.ClientGenerator._load_spec')
    def test_sanitize_name(self, mock_load_spec):
        """Test the _sanitize_name method."""
        mock_load_spec.return_value = self.test_spec
        generator = ClientGenerator("dummy_path.yaml", self.temp_dir)
        
        # Test various inputs
        self.assertEqual(generator._sanitize_name("test"), "test")
        self.assertEqual(generator._sanitize_name("Test Name"), "Test_Name")
        self.assertEqual(generator._sanitize_name("test-name"), "test_name")
        self.assertEqual(generator._sanitize_name("123test"), "api_123test")
        self.assertEqual(generator._sanitize_name("test!@#"), "test___")

    @patch('sap_hana_client_generator.generator.ClientGenerator._load_spec')
    def test_get_python_type(self, mock_load_spec):
        """Test the _get_python_type method."""
        mock_load_spec.return_value = self.test_spec
        generator = ClientGenerator("dummy_path.yaml", self.temp_dir)
        
        # Test various schema types
        self.assertEqual(generator._get_python_type({"type": "integer"}), "int")
        self.assertEqual(generator._get_python_type({"type": "number"}), "float")
        self.assertEqual(generator._get_python_type({"type": "boolean"}), "bool")
        self.assertEqual(generator._get_python_type({"type": "string"}), "str")
        self.assertEqual(
            generator._get_python_type({"type": "string", "format": "date-time"}),
            "datetime"
        )
        self.assertEqual(
            generator._get_python_type({"type": "array", "items": {"type": "string"}}),
            "List[str]"
        )
        self.assertEqual(
            generator._get_python_type({"type": "object"}),
            "Dict[str, Any]"
        )
        self.assertEqual(
            generator._get_python_type({"$ref": "#/components/schemas/TestModel"}),
            "TestModel"
        )
        self.assertEqual(generator._get_python_type({}), "Any")

    @patch('sap_hana_client_generator.generator.ClientGenerator')
    def test_generate_client_from_spec(self, mock_client_generator):
        """Test the generate_client_from_spec function."""
        mock_instance = MagicMock()
        mock_instance.generate.return_value = "/path/to/generated/client"
        mock_client_generator.return_value = mock_instance
        
        result = generate_client_from_spec("test_spec.yaml", "output_dir")
        
        mock_client_generator.assert_called_once_with("test_spec.yaml", "output_dir")
        mock_instance.generate.assert_called_once()
        self.assertEqual(result, "/path/to/generated/client")


if __name__ == '__main__':
    unittest.main() 