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

echo "Installing core dependencies from requirements.txt..."
echo ""

# Install core dependencies
if pip3 install -r requirements.txt; then
    echo ""
    echo "✅ Core dependencies installed successfully!"
else
    echo ""
    echo "❌ Failed to install core dependencies"
    echo "Please check the error messages above and try again"
    exit 1
fi

# Check for tkinter (GUI support)
echo ""
echo "Checking for GUI support (tkinter)..."
if python3 -c "import tkinter" 2>/dev/null; then
    echo "✅ GUI support available - you can use the graphical interface"
    echo "   Run: python3 autosort_gui.py"
    echo "   Or double-click: run-autosort-gui.command"
    GUI_AVAILABLE=true
else
    echo "⚠️  GUI support not available (tkinter missing)"
    echo ""
    
    # Check if this is macOS with Homebrew Python
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            PYTHON_PATH=$(which python3)
            if [[ "$PYTHON_PATH" == *"homebrew"* ]]; then
                echo "🔧 Detected macOS with Homebrew Python"
                echo "   Homebrew Python doesn't include tkinter by default"
                echo ""
                echo "   To enable GUI support, run:"
                echo "   brew install python-tk@3.13"
                echo ""
                echo "   Or install Python from python.org which includes tkinter"
                echo ""
                echo "   After installing tkinter, run this installer again"
            else
                echo "   To install tkinter on macOS:"
                echo "   - Install Python from python.org (includes tkinter)"
                echo "   - Or use Homebrew: brew install python-tk@3.13"
            fi
        else
            echo "   To install tkinter on macOS:"
            echo "   - Install Python from python.org (includes tkinter)"
            echo "   - Or install Homebrew and run: brew install python-tk@3.13"
        fi
    else
        echo "   To install tkinter on Linux:"
        echo "     Ubuntu/Debian: sudo apt-get install python3-tk"
        echo "     CentOS/RHEL: sudo yum install tkinter"
        echo "     Fedora: sudo dnf install python3-tkinter"
    fi
    
    echo ""
    echo "   You can still use the command-line version: python3 autosort.py"
    GUI_AVAILABLE=false
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Available options:"
echo "  Command Line: python3 autosort.py"
echo "  Double-click: run-autosort.command"
if [ "$GUI_AVAILABLE" = true ]; then
    echo "  GUI Version: python3 autosort_gui.py"
    echo "  Double-click: run-autosort-gui.command"
fi
echo ""
echo "Features available:"
echo "  ✅ File organization with 25+ categories"
echo "  ✅ Smart image subfolder organization"
echo "  ✅ Preview mode (dry run)"
echo "  ✅ Interactive configuration wizard"
if [ "$GUI_AVAILABLE" = true ]; then
    echo "  ✅ Graphical user interface"
else
    echo "  ⚠️  GUI not available (install tkinter to enable)"
fi
echo "  ✅ Progress tracking and statistics"
echo ""

echo "Press any key to exit..."
read -n 1
