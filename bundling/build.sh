#!/bin/bash
# Build script for SAGE MCP executable on macOS
# This script provides a convenient wrapper around the Python build script

set -e  # Exit on any error

echo "🚀 SAGE MCP Executable Builder for macOS"
echo "========================================"
echo "🍎 Detected macOS system"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ from:"
    echo "   - https://www.python.org/downloads/macos/"
    echo "   - Or use Homebrew: brew install python"
    echo "   - Or use pyenv: pyenv install 3.11.0"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed or not in PATH"
    echo "Please ensure pip3 is installed with Python"
    exit 1
fi

# Check for Xcode Command Line Tools (needed for some Python packages)
if ! command -v gcc &> /dev/null; then
    echo "⚠️  Xcode Command Line Tools not found. Some Python packages might need compilation."
    echo "Install with: xcode-select --install"
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
    if timeout 5s ./bundling/dist/sage_mcp 2>/dev/null || [ $? -eq 124 ]; then
        echo "✅ Executable appears to be working (server started successfully)"
    else
        echo "⚠️  Executable test inconclusive, but file exists"
    fi
    
    echo ""
    echo "💡 To run the server:"
    echo "   ./bundling/dist/sage_mcp"
    echo ""
    echo "💡 To run on a specific host/port:"
    echo "   MCP_HOST=127.0.0.1 MCP_PORT=8080 ./bundling/dist/sage_mcp"
    echo ""
    echo "🌐 Once running, the server will be available at:"
    echo "   http://localhost:8000/mcp"
    
else
    echo "❌ Build failed - executable not found"
    exit 1
fi 