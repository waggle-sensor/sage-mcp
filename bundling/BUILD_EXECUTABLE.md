# Building Sage MCP Server as Executable

This guide shows how to build the Sage MCP server as a standalone executable that can run without Python installation.

## Quick Start (macOS)

```bash
# Make sure all dependencies are installed
pip install -r requirements.txt
pip install pyinstaller

# Build the executable (automated)
./build.sh
```

The executable will be created at `dist/sage_mcp`.

## Manual Build Process

### 1. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Install PyInstaller
pip install pyinstaller
```

### 2. Build Using Python Script

```bash
python3 build_executable.py
```

### 3. Build Using PyInstaller Directly

```bash
# Create hooks directory and copy hook files
mkdir -p hooks
cp hook-*.py hooks/

# Build with spec file
pyinstaller --clean --onefile --console --name=sage_mcp --additional-hooks-dir=hooks sage_mcp.spec
```

## Running the Executable

### Basic Usage

```bash
# Run with default settings (binds to 0.0.0.0:8000)
./dist/sage_mcp
```

### Custom Host/Port

```bash
# Run on localhost only
MCP_HOST=127.0.0.1 ./dist/sage_mcp

# Run on custom port
MCP_PORT=8080 ./dist/sage_mcp

# Combine both
MCP_HOST=127.0.0.1 MCP_PORT=8080 ./dist/sage_mcp
```

### Background Execution

```bash
# Run in background
nohup ./dist/sage_mcp > sage_mcp.log 2>&1 &

# Check if running
ps aux | grep sage_mcp
```

## Accessing the Server

Once running, the MCP server will be available at:
- **HTTP endpoint**: `http://localhost:8000/mcp`
- **Health check**: `http://localhost:8000/mcp/`

## Troubleshooting

### Common Issues

1. **"No package metadata was found" errors**
   - This is fixed by the custom PyInstaller spec file and hooks
   - Make sure you're building with the provided `sage_mcp.spec` file

2. **Import errors for sage_mcp_server modules**
   - Ensure the `sage_mcp_server/` directory exists
   - The spec file includes this directory in the build

3. **Large executable size**
   - The executable includes all Python dependencies (~100-200MB)
   - This is normal for PyInstaller builds with scientific packages

4. **Permission denied on macOS**
   - Run: `chmod +x dist/sage_mcp`
   - Or: `xattr -d com.apple.quarantine dist/sage_mcp` (if downloaded)

### Debug Mode

To debug the executable:

```bash
# Build with debug mode
pyinstaller --debug=all sage_mcp.spec

# Run the debug version
./dist/sage_mcp
```

## Distribution

The executable is self-contained and can be distributed to other macOS machines without requiring Python installation.

### What's Included
- Python runtime
- All Python dependencies (pandas, numpy, fastmcp, etc.)
- Sage MCP server code
- All necessary libraries

### System Requirements
- macOS (built for the architecture you're building on)
- No Python installation required on target machine
- Network access for Sage API calls

## File Structure After Build

```
mcp/
├── dist/
│   └── sage_mcp              # The executable
├── build/                    # Build artifacts (can be deleted)
├── hooks/                    # PyInstaller hooks (auto-created)
├── sage_mcp.spec            # PyInstaller spec file
├── build_executable.py      # Python build script
├── build.sh                 # Shell build script (macOS)
└── BUILD_EXECUTABLE.md      # This file
```

## Advanced Configuration

### Custom PyInstaller Options

Edit `sage_mcp.spec` to customize:
- Executable name
- Icon file
- Excluded packages (to reduce size)
- Additional data files

### Environment Variables

The executable respects these environment variables:
- `MCP_HOST`: Server host (default: 0.0.0.0)
- `MCP_PORT`: Server port (default: 8000)
- `PYTHONUNBUFFERED`: Set to 1 for immediate output

## Performance Notes

- **Startup time**: ~2-5 seconds (vs ~1 second for Python script)
- **Memory usage**: Similar to Python script
- **File size**: ~100-200MB (includes full Python runtime)
- **Performance**: Identical to running the Python script directly

The slight startup delay is due to PyInstaller extracting the Python runtime and dependencies on first run.