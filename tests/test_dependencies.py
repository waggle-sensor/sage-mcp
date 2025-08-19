#!/usr/bin/env python3
"""
Dependency Test Script for SAGE MCP Server

This script verifies that all required dependencies are properly installed
before running the main server or building Docker containers.
"""

import sys
import importlib

def test_import(module_name, description=""):
    """Test if a module can be imported successfully"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name} - {description}")
        return True
    except ImportError as e:
        print(f"❌ {module_name} - {description}")
        print(f"   Error: {e}")
        return False

def main():
    """Test all required dependencies"""
    print("🧪 Testing SAGE MCP Server Dependencies")
    print("=" * 50)
    
    dependencies = [
        # Core MCP dependencies
        ("mcp", "Model Context Protocol"),
        ("fastmcp", "FastMCP server framework"),
        
        # Web framework dependencies
        ("fastapi", "FastAPI web framework"),
        ("uvicorn", "ASGI server"),
        ("starlette", "ASGI framework components"),
        ("starlette.responses", "Starlette response classes"),
        ("starlette.requests", "Starlette request classes"),
        
        # HTTP client
        ("httpx", "Async HTTP client"),
        ("requests", "HTTP client"),
        
        # SAGE data client
        ("sage_data_client", "SAGE data querying"),
        
        # Data processing
        ("pandas", "Data manipulation"),
        ("numpy", "Numerical computing"),
        
        # Configuration and serialization
        ("pydantic", "Data validation"),
        ("yaml", "YAML parsing"),
        
        # Standard library (should always work)
        ("json", "JSON handling"),
        ("asyncio", "Async programming"),
        ("logging", "Logging"),
        ("threading", "Threading"),
        ("uuid", "UUID generation"),
        ("datetime", "Date/time handling"),
        ("pathlib", "Path handling"),
        ("urllib.parse", "URL parsing"),
        ("contextvars", "Context variables"),
    ]
    
    failed = []
    passed = []
    
    for module, description in dependencies:
        if test_import(module, description):
            passed.append(module)
        else:
            failed.append(module)
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {len(passed)} passed, {len(failed)} failed")
    
    if failed:
        print(f"\n❌ Failed imports: {', '.join(failed)}")
        print("\n🔧 To fix missing dependencies, run:")
        print("pip install -r requirements.txt")
        print("\nOr install individually:")
        for module in failed:
            if module not in ['starlette.responses', 'starlette.requests']:
                print(f"pip install {module}")
        sys.exit(1)
    else:
        print("\n🎉 All dependencies are properly installed!")
        print("✅ Ready to run SAGE MCP Server!")
        
        # Test specific imports that the main server uses
        print("\n🔍 Testing specific server imports...")
        try:
            from fastmcp import FastMCP, Context
            from fastmcp.server.middleware import Middleware, MiddlewareContext
            from fastapi import HTTPException
            print("✅ FastMCP server components imported successfully")
            
            # Test sage_mcp_server imports
            from sage_mcp_server import SageDataService, SageJobService
            print("✅ SAGE MCP server components imported successfully")
            
            print("\n🚀 All systems ready for deployment!")
            
        except ImportError as e:
            print(f"❌ Server-specific import failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main() 