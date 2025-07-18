#!/bin/bash
# Dependency Management Script
# This script updates locked dependencies for reproducible builds

echo "Updating locked dependencies..."

# Generate locked requirements.txt from requirements.in
echo "Compiling production dependencies..."
pip-compile requirements.in --output-file requirements.txt

# Generate locked development dependencies
echo "Compiling development dependencies..."
pip-compile requirements-dev.in --output-file requirements-dev.txt

echo "Dependency locking complete!"
echo "Use 'pip install -r requirements.txt' for production"
echo "Use 'pip install -r requirements-dev.txt' for development"