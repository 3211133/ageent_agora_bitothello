#!/bin/bash
# Quick test runner with environment activation
# Usage: ./run_tests.sh [test_args]

if [ ! -f "venv/bin/activate" ]; then
    echo "❌ Virtual environment not found. Run ./scripts/dev-setup.sh first."
    exit 1
fi

source venv/bin/activate

if [ $# -eq 0 ]; then
    # Default: run all tests with coverage
    pytest --cov=src --cov-report=term-missing
else
    # Pass arguments to pytest
    pytest "$@"
fi
