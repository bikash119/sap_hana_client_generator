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
    def test_generate_tests(self, mock_load_spec):
        """Test test generation."""
        mock_load_spec.return_value = self.test_spec
        generator = ClientGenerator("dummy_path.yaml", self.temp_dir)
        
        # Create package structure first
        generator._create_package_structure()
        
        # Generate tests
        generator._generate_tests()
        
        # Check test files were created
        tests_dir = os.path.join(self.temp_dir, 'tests')
        self.assertTrue(os.path.exists(tests_dir))
        self.assertTrue(os.path.exists(os.path.join(tests_dir, '__init__.py')))
        self.assertTrue(os.path.exists(os.path.join(tests_dir, 'test_client.py')))
        self.assertTrue(os.path.exists(os.path.join(tests_dir, 'test_models.py')))
        self.assertTrue(os.path.exists(os.path.join(tests_dir, 'conftest.py')))

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
        
        # Test namespace handling
        self.assertEqual(generator._sanitize_name("API_SALES_ORDER_SRV.A_SalesOrderType"), 
                         "API_SALES_ORDER_SRV_A_SalesOrderType")
        self.assertEqual(generator._sanitize_name("namespace.subnamespace.Type"), 
                         "namespace_subnamespace_Type")
        self.assertEqual(generator._sanitize_name(".leadingDot"), 
                         "_leadingDot")  # Should handle leading dot
        self.assertEqual(generator._sanitize_name("trailingDot."), 
                         "trailingDot_")  # Should handle trailing dot

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
        
        # Test namespaced references
        self.assertEqual(
            generator._get_python_type({"$ref": "#/components/schemas/API_SALES_ORDER_SRV.A_SalesOrderType"}),
            "API_SALES_ORDER_SRV_A_SalesOrderType"
        )
        self.assertEqual(
            generator._get_python_type({"$ref": "#/components/schemas/ns1.ns2.Type"}),
            "ns1_ns2_Type"
        )
        
        # Test model reference tracking
        model_references = set()
        generator._get_python_type({"$ref": "#/components/schemas/TestModel"}, model_references)
        self.assertEqual(model_references, {"TestModel"})
        
        # Test tracking multiple references
        model_references = set()
        generator._get_python_type({"$ref": "#/components/schemas/Model1"}, model_references)
        generator._get_python_type({"$ref": "#/components/schemas/Model2"}, model_references)
        self.assertEqual(model_references, {"Model1", "Model2"})
        
        # Test tracking references in arrays
        model_references = set()
        generator._get_python_type(
            {"type": "array", "items": {"$ref": "#/components/schemas/ArrayItem"}},
            model_references
        )
        self.assertEqual(model_references, {"ArrayItem"})

    @patch('sap_hana_client_generator.generator.ClientGenerator._load_spec')
    def test_get_python_type_with_namespaces(self, mock_load_spec):
        """Test the _get_python_type method with namespaced references."""
        mock_load_spec.return_value = self.test_spec
        generator = ClientGenerator("dummy_path.yaml", self.temp_dir)
        
        # Test handling of namespaced references
        self.assertEqual(
            generator._get_python_type({"$ref": "#/components/schemas/API_SALES_ORDER_SRV.A_SalesOrderType"}),
            "API_SALES_ORDER_SRV_A_SalesOrderType"
        )
        
        # Test with multiple namespace levels
        self.assertEqual(
            generator._get_python_type({"$ref": "#/components/schemas/ns1.ns2.Type"}),
            "ns1_ns2_Type"
        )
        
        # Test with a mix of reference and other properties
        complex_schema = {
            "$ref": "#/components/schemas/API_SALES_ORDER_SRV.A_SalesOrderType",
            "description": "A sales order"
        }
        self.assertEqual(
            generator._get_python_type(complex_schema),
            "API_SALES_ORDER_SRV_A_SalesOrderType"
        )

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