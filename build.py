#!/usr/bin/env python3
"""
Simple build script for SAGE MCP executable.
This script changes to the bundling directory and runs the cross-platform build.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Change to bundling directory and run the build."""
    print("🚀 SAGE MCP Build Script")
    print("========================")
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    bundling_dir = script_dir / "bundling"
    
    # Check if bundling directory exists
    if not bundling_dir.exists():
        print("❌ Error: bundling directory not found")
        print(f"   Expected: {bundling_dir}")
        sys.exit(1)
    
    # Check if build_executable.py exists
    build_script = bundling_dir / "build_executable.py"
    if not build_script.exists():
        print("❌ Error: build_executable.py not found in bundling directory")
        sys.exit(1)
    
    print(f"📁 Changing to bundling directory: {bundling_dir}")
    
    # Change to bundling directory and run the build
    try:
        # Determine Python command based on platform
        python_cmd = "python" if sys.platform == "win32" else "python3"
        
        # Run the build script
        result = subprocess.run(
            [python_cmd, "build_executable.py"],
            cwd=bundling_dir,
            check=True
        )
        
        print("\n✅ Build completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with exit code {e.returncode}")
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("❌ Error: Python not found in PATH")
        print("Please ensure Python 3.8+ is installed and in your PATH")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 