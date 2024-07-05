#!/bin/bash

# Please ensure you're in the root directory of the repository before running this script.

# Install coverage if not already installed
pip install coverage

# Run tests with coverage
PYTHONPATH=./lib coverage run -m unittest discover tests/

# Generate coverage report
coverage report -m

# Generate HTML coverage report
coverage html

echo "HTML coverage report generated in htmlcov/index.html"