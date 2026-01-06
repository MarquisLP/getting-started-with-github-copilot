#!/bin/bash
# Script to run pytest tests

echo "Running tests..."
python3 -m pytest tests/ -v --tb=short

echo ""
echo "Test run complete!"
