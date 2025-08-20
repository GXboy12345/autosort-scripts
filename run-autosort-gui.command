#!/usr/bin/env bash

# Set error handling
set -e  # Exit on any error
set -u  # Exit on undefined variables

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a directory exists
directory_exists() {
    [ -d "$1" ]
}

# Function to check if a file exists
file_exists() {
    [ -f "$1" ]
}

# Main execution
main() {
    print_status "Starting AutoSort GUI..."
    
    # Define the script directory
    SCRIPT_DIR="$HOME/Desktop/Autosortscripts"
    PYTHON_SCRIPT="$SCRIPT_DIR/autosort.py"
    
    print_status "Script directory: $SCRIPT_DIR"
    
    # Check if Python3 is available
    if ! command_exists python3; then
        print_error "Python3 is not installed or not in PATH"
        print_status "Please install Python3 from https://www.python.org/downloads/"
        exit 1
    fi
    
    print_success "Python3 found: $(python3 --version)"
    
    # Check if the script directory exists
    if ! directory_exists "$SCRIPT_DIR"; then
        print_error "Script directory does not exist: $SCRIPT_DIR"
        print_status "Please ensure the AutoSort scripts are in the correct location"
        exit 1
    fi
    
    print_success "Script directory found"
    
    # Check if the Python script exists
    if ! file_exists "$PYTHON_SCRIPT"; then
        print_error "Python script not found: $PYTHON_SCRIPT"
        print_status "Please ensure autosort.py is in the script directory"
        exit 1
    fi
    
    print_success "Python script found"
    
    # Check if we have read and execute permissions for the script
    if ! [ -r "$PYTHON_SCRIPT" ] || ! [ -x "$PYTHON_SCRIPT" ]; then
        print_warning "Setting execute permissions on autosort.py..."
        chmod +x "$PYTHON_SCRIPT"
    fi
    
    # Check if tkinter is available
    if ! python3 -c "import tkinter" 2>/dev/null; then
        print_error "tkinter is not available"
        print_status "Please install tkinter or use the command line version (autosort.py)"
        exit 1
    fi
    
    print_success "tkinter found"
    
    # Change to the script directory
    print_status "Changing to script directory..."
    cd "$SCRIPT_DIR" || {
        print_error "Failed to change to script directory"
        exit 1
    }
    
    print_success "Changed to script directory: $(pwd)"
    
    # Run the Python script with GUI flag
    print_status "Launching AutoSort GUI..."
    if python3 ./autosort.py --gui; then
        print_success "AutoSort GUI completed successfully"
        exit 0
    else
        print_error "AutoSort GUI failed with exit code $?"
        exit 1
    fi
}

# Handle script interruption
trap 'print_error "Script interrupted by user"; exit 1' INT TERM

# Run the main function
main "$@"
