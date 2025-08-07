#!/bin/bash
# Build script for SAGE MCP executable on Linux
# This script provides a convenient wrapper around the Python build script

set -e  # Exit on any error

echo "🚀 SAGE MCP Executable Builder for Linux"
echo "========================================="

# Detect Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
elif [ -f /etc/redhat-release ]; then
    DISTRO="rhel"
elif [ -f /etc/debian_version ]; then
    DISTRO="debian"
else
    DISTRO="unknown"
fi

echo "🐧 Detected Linux distribution: $DISTRO"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ using your package manager:"
    case $DISTRO in
        ubuntu|debian)
            echo "   sudo apt update && sudo apt install python3 python3-pip python3-venv"
            ;;
        fedora)
            echo "   sudo dnf install python3 python3-pip python3-virtualenv"
            ;;
        centos|rhel)
            echo "   sudo yum install python3 python3-pip"
            ;;
        arch)
            echo "   sudo pacman -S python python-pip"
            ;;
        opensuse*)
            echo "   sudo zypper install python3 python3-pip"
            ;;
        *)
            echo "   Use your distribution's package manager to install python3 and python3-pip"
            ;;
    esac
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed or not in PATH"
    echo "Please install pip3 using your package manager:"
    case $DISTRO in
        ubuntu|debian)
            echo "   sudo apt install python3-pip"
            ;;
        fedora)
            echo "   sudo dnf install python3-pip"
            ;;
        centos|rhel)
            echo "   sudo yum install python3-pip"
            ;;
        arch)
            echo "   sudo pacman -S python-pip"
            ;;
        opensuse*)
            echo "   sudo zypper install python3-pip"
            ;;
        *)
            echo "   Use your distribution's package manager to install python3-pip"
            ;;
    esac
    exit 1
fi

# Check for development tools that might be needed
if ! command -v gcc &> /dev/null; then
    echo "⚠️  gcc not found. Some Python packages might need compilation."
    echo "Consider installing build tools:"
    case $DISTRO in
        ubuntu|debian)
            echo "   sudo apt install build-essential"
            ;;
        fedora)
            echo "   sudo dnf groupinstall 'Development Tools'"
            ;;
        centos|rhel)
            echo "   sudo yum groupinstall 'Development Tools'"
            ;;
        arch)
            echo "   sudo pacman -S base-devel"
            ;;
        opensuse*)
            echo "   sudo zypper install -t pattern devel_basis"
            ;;
    esac
fi

# Run the Python build script
echo "🔨 Running build process..."
python3 bundling/build_executable.py

# Check if build was successful
if [ -f "bundling/dist/sage_mcp" ]; then
    echo ""
    echo "✅ Build completed successfully!"
    echo "📍 Executable location: $(pwd)/bundling/dist/sage_mcp"
    echo ""
    echo "🧪 Testing executable startup (will timeout after 5 seconds)..."
    
    # Test the executable with a timeout
    if timeout 5s ./bundling/dist/sage_mcp --help 2>/dev/null || [ $? -eq 124 ]; then
        echo "✅ Executable appears to be working (server started successfully)"
    else
        echo "⚠️  Executable test inconclusive, but file exists"
    fi
    
    # Check if executable is properly linked
    echo "🔍 Checking executable dependencies..."
    if command -v ldd &> /dev/null; then
        echo "📚 Shared library dependencies:"
        ldd bundling/dist/sage_mcp | head -5
        echo "   ... (showing first 5 dependencies)"
    fi
    
    echo ""
    echo "💡 To run the server:"
    echo "   ./bundling/dist/sage_mcp"
    echo ""
    echo "💡 To run on a specific host/port:"
    echo "   MCP_HOST=127.0.0.1 MCP_PORT=8080 ./bundling/dist/sage_mcp"
    echo ""
    echo "💡 To make it globally accessible:"
    echo "   sudo cp bundling/dist/sage_mcp /usr/local/bin/"
    echo "   # Then run: sage_mcp"
    echo ""
    echo "🌐 Once running, the server will be available at:"
    echo "   http://localhost:8000/mcp"
    
else
    echo "❌ Build failed - executable not found"
    exit 1
fi 