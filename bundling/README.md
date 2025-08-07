# SAGE MCP Executable Bundling

This directory contains all files related to creating standalone executable versions of the SAGE MCP server using PyInstaller.

## Files Overview

- `build_executable.py` - Main Python script for building the executable
- `build.sh` - Shell script wrapper for the build process (macOS/Linux)
- `sage_mcp.spec` - PyInstaller specification file
- `hook-fastmcp.py` - PyInstaller hook for fastmcp package
- `hook-sage_data_client.py` - PyInstaller hook for sage_data_client package
- `hooks/` - Directory containing PyInstaller hooks
- `BUILD_EXECUTABLE.md` - Detailed build instructions
- `README-EXECUTABLE.md` - Usage instructions for the executable

## Quick Build

### Prerequisites
- Python 3.8+
- PyInstaller (`pip install pyinstaller`)
- All project dependencies installed

### Build Command

From the project root directory:

```bash
# Using the shell script (recommended)
./bundling/build.sh

# Or directly with Python
python bundling/build_executable.py
```

The executable will be created at `bundling/dist/sage_mcp`.

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