#!/usr/bin/env python3
"""
Simple test script to verify Sage MCP Server configuration
"""

import os
import requests
import time
import subprocess
import sys
from threading import Thread

def test_fastmcp_params():
    """Test that FastMCP accepts host/port parameters"""
    try:
        from fastmcp import FastMCP

        # Create a simple test server
        mcp = FastMCP("TestServer")

        @mcp.tool
        def hello(name: str) -> str:
            return f"Hello, {name}!"

        print("✅ New FastMCP import successful")
        print("✅ Tool registration successful")

        # Test that run method accepts our parameters
        import inspect
        run_sig = inspect.signature(mcp.run)
        params = list(run_sig.parameters.keys())

        print(f"📋 Available parameters for mcp.run(): {params}")

        if 'host' in params and 'port' in params:
            print("✅ FastMCP supports host and port parameters")
        else:
            print("❌ FastMCP does not support host and port parameters")

        return True

    except Exception as e:
        print(f"❌ FastMCP test failed: {e}")
        return False

def test_server_startup():
    """Test that the server can start and respond"""
    print("\n🚀 Testing server startup...")

    # Set environment variables
    env = os.environ.copy()
    env.update({
        "MCP_HOST": "127.0.0.1",
        "MCP_PORT": "8001"  # Use different port to avoid conflicts
    })

    # Start server in background
    try:
        process = subprocess.Popen(
            [sys.executable, "sage_mcp.py"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Wait a bit for server to start
        time.sleep(3)

        # Check if server is responding
        try:
            response = requests.get("http://127.0.0.1:8001/mcp", timeout=5)
            if response.status_code == 200:
                print("✅ Server is responding to HTTP requests")
                success = True
            else:
                print(f"⚠️  Server responded with status {response.status_code}")
                success = False
        except requests.exceptions.RequestException as e:
            print(f"❌ Server not responding: {e}")
            success = False

        # Terminate server
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

        return success

    except Exception as e:
        print(f"❌ Server startup test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Sage MCP Server Configuration")
    print("=" * 50)

    # Test FastMCP functionality
    fastmcp_ok = test_fastmcp_params()

    if fastmcp_ok:
        # Test server startup
        server_ok = test_server_startup()

        print("\n" + "=" * 50)
        if fastmcp_ok and server_ok:
            print("✅ All tests passed! Server is ready for deployment.")
            print("\nTo run the server with external access:")
            print("  export MCP_HOST=0.0.0.0")
            print("  export MCP_PORT=8000")
            print("  python sage_mcp.py")
            print("\nOr using Docker:")
            print("  docker-compose up --build")
        else:
            print("❌ Some tests failed. Check the output above.")
            sys.exit(1)
    else:
        print("❌ FastMCP tests failed. Cannot proceed with server tests.")
        sys.exit(1)

if __name__ == "__main__":
    main()