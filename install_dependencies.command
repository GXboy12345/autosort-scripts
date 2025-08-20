#!/bin/bash
# AutoSort Dependencies Installer
# This script installs the required dependencies for AutoSort

echo "AutoSort Dependencies Installer"
echo "================================"
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.6+ from https://www.python.org/downloads/"
    exit 1
fi

echo "Python 3 found: $(python3 --version)"
echo ""

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not available"
    echo "Please ensure pip is installed with your Python installation"
    exit 1
fi

echo "Installing dependencies from requirements.txt..."
echo ""

# Install dependencies
if pip3 install -r requirements.txt; then
    echo ""
    echo "✅ Dependencies installed successfully!"
    echo ""
    echo "You can now run AutoSort with:"
    echo "  python3 autosort.py"
    echo ""
    echo "Or double-click run-autosort.command"
else
    echo ""
    echo "❌ Failed to install dependencies"
    echo "Please check the error messages above and try again"
    exit 1
fi

echo "Press any key to exit..."
read -n 1
