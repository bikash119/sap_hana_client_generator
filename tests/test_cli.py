"""Tests for the CLI module."""

import unittest
from unittest.mock import patch, MagicMock

from sap_hana_client_generator.cli import parse_args, main


class TestCLI(unittest.TestCase):
    """Test cases for the CLI module."""

    def test_parse_args(self):
        """Test the parse_args function."""
        # Test with required arguments only
        args = parse_args(['spec.yaml'])
        self.assertEqual(args.spec_path, 'spec.yaml')
        self.assertIsNone(args.output_dir)
        self.assertFalse(args.verbose)
        
        # Test with all arguments
        args = parse_args(['spec.yaml', '--output-dir', 'output', '--verbose'])
        self.assertEqual(args.spec_path, 'spec.yaml')
        self.assertEqual(args.output_dir, 'output')
        self.assertTrue(args.verbose)
        
        # Test with short options
        args = parse_args(['spec.yaml', '-o', 'output', '-v'])
        self.assertEqual(args.spec_path, 'spec.yaml')
        self.assertEqual(args.output_dir, 'output')
        self.assertTrue(args.verbose)

    @patch('sap_hana_client_generator.cli.generate_client_from_spec')
    @patch('sap_hana_client_generator.cli.setup_logging')
    def test_main_success(self, mock_setup_logging, mock_generate):
        """Test the main function with successful execution."""
        mock_generate.return_value = '/path/to/output'
        
        result = main(['spec.yaml', '--output-dir', 'output'])
        
        mock_setup_logging.assert_called_once_with(False)
        mock_generate.assert_called_once_with('spec.yaml', 'output')
        self.assertEqual(result, 0)

    @patch('sap_hana_client_generator.cli.generate_client_from_spec')
    @patch('sap_hana_client_generator.cli.setup_logging')
    def test_main_error(self, mock_setup_logging, mock_generate):
        """Test the main function with an error."""
        mock_generate.side_effect = ValueError("Test error")
        
        result = main(['spec.yaml'])
        
        mock_setup_logging.assert_called_once_with(False)
        mock_generate.assert_called_once_with('spec.yaml', None)
        self.assertEqual(result, 1)


if __name__ == '__main__':
    unittest.main() 