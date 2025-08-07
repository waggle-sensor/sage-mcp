# SAGE MCP Server Executable

This is a standalone executable of the SAGE MCP (Model Context Protocol) Server.

## Quick Start

### Option 1: Use the run script
- **Windows**: Double-click `run-sage-mcp-server.bat`
- **macOS/Linux**: Run `./run-sage-mcp-server.sh`

### Option 2: Run directly
- **Windows**: `dist\sage-mcp-server.exe`
- **macOS/Linux**: `./dist/sage-mcp-server`

## Usage

Once started, the server will be available at:
- **HTTP**: http://localhost:8000/mcp

The server provides tools for:
- Querying SAGE sensor data
- Submitting and managing jobs on SAGE nodes
- Accessing documentation and help
- Finding and working with plugins

## Configuration

The server can be configured using environment variables:
- `MCP_HOST`: Host to bind to (default: 0.0.0.0)
- `MCP_PORT`: Port to listen on (default: 8000)

Example:
```bash
# Windows
set MCP_HOST=127.0.0.1
set MCP_PORT=9000
dist\sage-mcp-server.exe

# macOS/Linux
MCP_HOST=127.0.0.1 MCP_PORT=9000 ./dist/sage-mcp-server
```

## Troubleshooting

If you encounter issues:

1. **Port already in use**: Change the port using `MCP_PORT` environment variable
2. **Permission denied**: On macOS/Linux, ensure the executable has execute permissions:
   ```bash
   chmod +x dist/sage-mcp-server
   ```
3. **Network issues**: Try binding to localhost only:
   ```bash
   MCP_HOST=127.0.0.1 ./dist/sage-mcp-server
   ```

## System Requirements

- No Python installation required (executable is self-contained)
- Internet connection for accessing SAGE data
- Available port (default 8000)

## Source Code

This executable was built from the SAGE MCP Server source code.
Visit the repository for the latest updates and documentation.
