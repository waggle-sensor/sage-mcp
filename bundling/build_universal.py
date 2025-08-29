#!/usr/bin/env python3
"""
Universal build script for Sage MCP executable.
This script detects the platform and runs the appropriate build process.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def detect_platform():
    """Detect the current platform and return appropriate script info."""
    system = platform.system().lower()

    if system == 'windows':
        return {
            'platform': 'Windows',
            'script': 'build.bat',
            'python_build': True,  # Can use Python build directly
            'icon': '🪟'
        }
    elif system == 'darwin':
        return {
            'platform': 'macOS',
            'script': 'build.sh',
            'python_build': True,  # Can use Python build directly
            'icon': '🍎'
        }
    elif system == 'linux':
        return {
            'platform': 'Linux',
            'script': 'build_linux.sh',
            'python_build': True,  # Can use Python build directly
            'icon': '🐧'
        }
    else:
        return {
            'platform': system,
            'script': None,
            'python_build': True,  # Fallback to Python build
            'icon': '🖥️'
        }

def main():
    """Main function to run the appropriate build script."""
    platform_info = detect_platform()

    print(f"🚀 Sage MCP Universal Build Script")
    print(f"==================================")
    print(f"{platform_info['icon']} Detected platform: {platform_info['platform']}")
    print()

    # Check if we're in the right directory
    if not Path('build_executable.py').exists():
        print("❌ Error: This script must be run from the bundling directory")
        print("   cd bundling && python build_universal.py")
        sys.exit(1)

    # Option 1: Always use the Python build script (recommended)
    if platform_info['python_build']:
        print("🔨 Using cross-platform Python build script...")
        try:
            # Import and run the build script directly
            sys.path.insert(0, '.')
            import build_executable
            build_executable.main()
        except ImportError:
            # Fallback to subprocess call
            python_cmd = 'python' if platform_info['platform'] == 'Windows' else 'python3'
            subprocess.run([python_cmd, 'build_executable.py'], check=True)

    # Option 2: Use platform-specific scripts (if they exist and user prefers)
    elif platform_info['script'] and Path(platform_info['script']).exists():
        print(f"🔨 Using platform-specific script: {platform_info['script']}")
        if platform_info['platform'] == 'Windows':
            subprocess.run([platform_info['script']], shell=True, check=True)
        else:
            subprocess.run(['bash', platform_info['script']], check=True)

    else:
        print("⚠️  No platform-specific script found, falling back to Python build...")
        python_cmd = 'python' if platform_info['platform'] == 'Windows' else 'python3'
        subprocess.run([python_cmd, 'build_executable.py'], check=True)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Build cancelled by user")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with exit code {e.returncode}")
        sys.exit(e.returncode)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)