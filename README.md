# SAGE MCP Server

A Model Context Protocol (MCP) server for the SAGE (Sensing at the Edge) platform.

## Project Structure

```
.
├── sage_mcp.py              # Main MCP server entry point
├── sage_mcp_server/         # Core package containing server components
│   ├── __init__.py         # Package initialization with clean exports
│   ├── models.py           # Data models and type definitions
│   ├── utils.py            # Utility functions
│   ├── data_service.py     # Data access and query service
│   ├── job_service.py      # Job submission and management
│   ├── job_templates.py    # Job template definitions
│   ├── docs_helper.py      # Documentation and help system
│   ├── plugin_metadata.py  # Plugin metadata and registry
│   ├── plugin_query_service.py  # Plugin search and query
│   ├── plugin_generator.py # Plugin generation utilities
│   └── plugin_registry.py  # Plugin registry classes
├── bundling/               # Executable building tools (PyInstaller)
│   ├── build.sh           # Build script for creating executables
│   ├── build_executable.py # PyInstaller build configuration
│   ├── sage_mcp.spec      # PyInstaller specification file
│   ├── hook-*.py          # PyInstaller hooks for dependencies
│   └── README.md          # Bundling documentation
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container deployment configuration
├── docker-compose.yml     # Docker orchestration
├── GETTING_STARTED.md     # Comprehensive user guide
└── README.md              # This file
```

## Installation & Deployment

### Option 1: Python Development
```bash
pip install -r requirements.txt
python3 sage_mcp.py
```

### Option 2: Docker (Recommended for Production)
```bash
# Using docker-compose
docker-compose up -d

# Or manually
docker build -t sage-mcp-server .
docker run -p 8000:8000 sage-mcp-server
```

### Option 3: Standalone Executable
```bash
# Build executable (includes all dependencies)
./bundling/build.sh

# Run on any machine (no Python required)
./bundling/dist/sage_mcp
```

## Features

- **Clean Architecture**: Modular design with organized packages
- **Plugin System**: Extensible plugin architecture for SAGE nodes
- **Job Management**: Submit and manage jobs on SAGE infrastructure
- **Data Access**: Query sensor data and measurements
- **Documentation**: Built-in help and documentation system

## API

The server exposes MCP tools for:
- Node management and discovery
- Sensor data queries
- Job submission and monitoring
- Plugin management
- Documentation access

## Development

The project uses a clean package structure with:
- All imports centralized in `sage_mcp_server/__init__.py`
- Modular components in the `sage_mcp_server/` package
- Main server logic in `sage_mcp.py`

## Changes Made

This repository has been cleaned up and reorganized:

1. **Removed unused files**: Eliminated test files, standalone scripts, and documentation that wasn't needed by the main server
2. **Created package structure**: Organized core components into `sage_mcp_server/` package
3. **Clean imports**: Centralized all imports in the package `__init__.py`
4. **Docker support**: Added proper Dockerfile for Linux deployment
5. **Documentation**: Created this README for the new structure

The server is now ready for production deployment with a clean, maintainable structure. 