"""Command-line interface for SAP HANA client generator.

This module provides a command-line interface for generating Python client libraries
from OpenAPI specifications.
"""

import argparse
import logging
import sys
from typing import List, Optional
from .generator import generate_client_from_spec

logger = logging.getLogger(__name__)

def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration.
    
    Args:
        verbose: Whether to enable verbose logging
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments.
    
    Args:
        args: Command-line arguments to parse. If None, sys.argv is used.
        
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Generate a Python client library from an OpenAPI specification"
    )
    
    parser.add_argument(
        "spec_path",
        help="Path to the OpenAPI specification file (JSON or YAML)"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        help="Directory where the generated client library will be saved"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args(args)

def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the command-line interface.
    
    Args:
        args: Command-line arguments. If None, sys.argv is used.
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parsed_args = parse_args(args)
    setup_logging(parsed_args.verbose)
    
    try:
        output_dir = generate_client_from_spec(
            parsed_args.spec_path,
            parsed_args.output_dir
        )
        logger.info(f"Client library generated successfully at: {output_dir}")
        return 0
    except Exception as e:
        logger.error(f"Error generating client library: {e}")
        if parsed_args.verbose:
            logger.exception("Detailed error information:")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 