#!/usr/bin/env bash

# AutoSort - Dependency Installer
# ===============================
# This script automatically installs the required dependencies for AutoSort
# Works with both system Python and Homebrew-managed Python environments

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

# Function to detect Python environment
detect_python_env() {
    local python_cmd="$1"
    local python_path
    
    if command_exists "$python_cmd"; then
        python_path=$(which "$python_cmd")
        
        # Check if it's a Homebrew Python
        if [[ "$python_path" == *"/opt/homebrew/"* ]] || [[ "$python_path" == *"/usr/local/"* ]]; then
            echo "homebrew"
        else
            echo "system"
        fi
    else
        echo "not_found"
    fi
}

# Function to install dependencies
install_dependencies() {
    local python_cmd="$1"
    local env_type="$2"
    
    print_status "Installing dependencies using $python_cmd ($env_type Python)..."
    
    # Check if pip is available
    if ! "$python_cmd" -m pip --version >/dev/null 2>&1; then
        print_error "pip not available for $python_cmd"
        print_status "Please install pip first: https://pip.pypa.io/en/stable/installation/"
        return 1
    fi
    
    # Try different installation methods based on environment
    if [ "$env_type" = "homebrew" ]; then
        print_status "Homebrew Python detected - using --user flag for safe installation..."
        
        # Try with --user flag first
        if "$python_cmd" -m pip install --user -r requirements.txt; then
            print_success "Dependencies installed successfully to user directory!"
            return 0
        else
            print_warning "User installation failed, trying with --break-system-packages..."
            if "$python_cmd" -m pip install --break-system-packages -r requirements.txt; then
                print_success "Dependencies installed successfully!"
                return 0
            else
                print_error "Failed to install dependencies"
                print_status "Consider using a virtual environment or pipx"
                return 1
            fi
        fi
    else
        # System Python - try normal installation
        print_status "System Python detected - attempting normal installation..."
        
        # Upgrade pip first
        print_status "Upgrading pip..."
        "$python_cmd" -m pip install --upgrade pip
        
        # Install requirements
        print_status "Installing AutoSort dependencies..."
        if "$python_cmd" -m pip install -r requirements.txt; then
            print_success "Dependencies installed successfully!"
            return 0
        else
            print_error "Failed to install dependencies"
            return 1
        fi
    fi
}

# Main execution
main() {
    print_status "AutoSort Dependency Installer"
    print_status "============================="
    echo ""
    
    # Get the script directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    print_status "Script directory: $SCRIPT_DIR"
    
    # Check if requirements.txt exists
    if ! file_exists "$SCRIPT_DIR/requirements.txt"; then
        print_error "requirements.txt not found in $SCRIPT_DIR"
        print_status "Please ensure you're running this from the AutoSort directory"
        exit 1
    fi
    
    print_success "Found requirements.txt"
    
    # Change to script directory
    cd "$SCRIPT_DIR" || {
        print_error "Failed to change to script directory"
        exit 1
    }
    
    # Detect Python environments
    print_status "Detecting Python environments..."
    
    PYTHON3_ENV=$(detect_python_env "python3")
    PYTHON_ENV=$(detect_python_env "python")
    
    # Determine which Python to use
    if [ "$PYTHON3_ENV" != "not_found" ]; then
        PYTHON_CMD="python3"
        PYTHON_ENV_TYPE="$PYTHON3_ENV"
        PYTHON_PATH=$(which python3)
        print_success "Using python3 ($PYTHON_ENV_TYPE) at: $PYTHON_PATH"
    elif [ "$PYTHON_ENV" != "not_found" ]; then
        PYTHON_CMD="python"
        PYTHON_ENV_TYPE="$PYTHON_ENV"
        PYTHON_PATH=$(which python)
        print_success "Using python ($PYTHON_ENV_TYPE) at: $PYTHON_PATH"
    else
        print_error "No Python installation found"
        print_status "Please install Python 3.8+ from https://www.python.org/downloads/"
        print_status "Or install via Homebrew: brew install python"
        exit 1
    fi
    
    # Show Python version
    PYTHON_VERSION=$("$PYTHON_CMD" --version 2>&1)
    print_status "Python version: $PYTHON_VERSION"
    
    # Check Python version compatibility
    PYTHON_MAJOR=$("$PYTHON_CMD" -c "import sys; print(sys.version_info.major)")
    PYTHON_MINOR=$("$PYTHON_CMD" -c "import sys; print(sys.version_info.minor)")
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        print_error "Python 3.8+ required, found $PYTHON_VERSION"
        print_status "Please upgrade your Python installation"
        exit 1
    fi
    
    print_success "Python version is compatible"
    
    # Install dependencies
    if install_dependencies "$PYTHON_CMD" "$PYTHON_ENV_TYPE"; then
        echo ""
        print_success "🎉 All dependencies installed successfully!"
        print_status "You can now run AutoSort:"
        echo ""
        print_status "  Command line: ./run-autosort.command"
        print_status "  GUI version:  ./run-autosort-gui.command"
        echo ""
        print_status "Or directly with Python:"
        print_status "  python3 autosort.py"
        print_status "  python3 autosort.py --gui"
        echo ""
        exit 0
    else
        print_error "❌ Failed to install dependencies"
        echo ""
        print_status "You can try installing manually:"
        print_status "  $PYTHON_CMD -m pip install -r requirements.txt"
        echo ""
        exit 1
    fi
}

# Handle script interruption
trap 'print_error "Installation interrupted by user"; exit 1' INT TERM

# Run the main function
main "$@"
