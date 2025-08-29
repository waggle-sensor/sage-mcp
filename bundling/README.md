# Sage MCP Cross-Platform Executable Bundling

This directory contains all files related to creating standalone executable versions of the Sage MCP server using PyInstaller for **Windows**, **macOS**, and **Linux**.

## Files Overview

### Core Build Files
- `build_executable.py` - **Main cross-platform Python build script** (recommended)
- `build_universal.py` - Universal build script that detects platform and runs appropriate build
- `sage_mcp.spec` - PyInstaller specification file with cross-platform support

### Platform-Specific Scripts
- `build.sh` - macOS build script wrapper 🍎
- `build_linux.sh` - Linux build script wrapper 🐧
- `build.bat` - Windows build script wrapper 🪟

### PyInstaller Hooks
- `hook-fastmcp.py` - PyInstaller hook for fastmcp package
- `hook-sage_data_client.py` - PyInstaller hook for sage_data_client package
- `hooks/` - Directory containing PyInstaller hooks

### Documentation
- `BUILD_EXECUTABLE.md` - Detailed build instructions
- `README-EXECUTABLE.md` - Usage instructions for the executable

## Quick Build (Cross-Platform)

### Prerequisites
- Python 3.8+
- All project dependencies installed (`pip install -r requirements.txt`)
- PyInstaller will be automatically installed if needed

### Build Commands

**Option 1: Universal Python Script (Recommended)**
```bash
# From the project root directory - works on all platforms
python bundling/build_executable.py

# Or use the universal wrapper
python bundling/build_universal.py
```

**Option 2: Platform-Specific Scripts**
```bash
# macOS/Linux
./bundling/build.sh           # macOS
./bundling/build_linux.sh     # Linux

# Windows (Command Prompt or PowerShell)
bundling\build.bat
```

### Output Files
- **Windows**: `bundling/dist/sage_mcp.exe`
- **macOS/Linux**: `bundling/dist/sage_mcp`

## Output Structure

After building, the directory structure will be:
```
bundling/
├── build/          # Temporary build files (auto-generated)
├── dist/           # Final executable output
│   └── sage_mcp    # The standalone executable
├── hooks/          # PyInstaller hooks
└── ...             # Source files
```

## Running the Executable

```bash
# Run with defaults (binds to 0.0.0.0:8000)
./bundling/dist/sage_mcp

# Run with custom host/port
MCP_HOST=127.0.0.1 MCP_PORT=8080 ./bundling/dist/sage_mcp
```

## Notes

- The executable is self-contained and includes all Python dependencies
- No Python installation is required on target machines
- The executable size is typically 100-200MB due to included libraries
- Build artifacts in `build/` and `dist/` are automatically cleaned before each build
- Hooks ensure proper inclusion of fastmcp and sage_data_client packages

## Troubleshooting

If the build fails:
1. Ensure all dependencies are installed: `pip install -r ../requirements.txt`
2. Check that PyInstaller is installed: `pip install pyinstaller`
3. Run from the project root directory, not from the bundling directory
4. Check the console output for specific error messages

For runtime issues with the executable:
1. Test that the regular Python script works: `python ../sage_mcp.py`
2. Check environment variables are set correctly
3. Ensure network ports are available
4. Run with verbose output to debug startup issues