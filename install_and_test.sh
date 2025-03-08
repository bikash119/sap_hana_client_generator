#!/bin/bash
# Script to install and test the SAP HANA Client Generator package

set -e  # Exit on error

echo "Installing the package in development mode..."
pip install -e .

echo "Running tests..."
python -m unittest discover -s tests

echo "Running the example script..."
python example.py

echo "Installation and testing completed successfully!" 