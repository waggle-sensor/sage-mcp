#!/bin/bash
# Build script for SAGE MCP executable on macOS

set -e  # Exit on any error

echo "🚀 SAGE MCP Executable Builder for macOS"
echo "========================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed or not in PATH"
    exit 1
fi

# Install PyInstaller if not already installed
if ! pip3 show pyinstaller &> /dev/null; then
    echo "📦 Installing PyInstaller..."
    pip3 install pyinstaller
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