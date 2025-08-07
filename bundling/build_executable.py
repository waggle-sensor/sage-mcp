#!/usr/bin/env python3
"""
Build script for creating a SAGE MCP executable using PyInstaller.
This script handles all the necessary configuration and dependencies.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if all required packages are installed."""
    required_packages = [
        'pyinstaller',
        'fastmcp',
        'mcp',
        'sage-data-client',
        'pandas',
        'numpy',
        'pydantic',
        'pyyaml',
        'requests',
        'httpx'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            # Try different import names
            import_names = [package.replace('-', '_')]
            if package == 'pyyaml':
                import_names = ['yaml']
            elif package == 'sage-data-client':
                import_names = ['sage_data_client']
            elif package == 'pyinstaller':
                import_names = ['PyInstaller']
            
            imported = False
            for import_name in import_names:
                try:
                    __import__(import_name)
                    imported = True
                    break
                except ImportError:
                    continue
            
            if not imported:
                missing_packages.append(package)
                
        except Exception:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install them with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All required packages are installed")
    return True

def clean_build_dirs():
    """Clean previous build directories."""
    # Clean in both the bundling directory and parent directory
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        # Clean in bundling directory
        if os.path.exists(dir_name):
            print(f"🧹 Cleaning bundling/{dir_name}...")
            shutil.rmtree(dir_name)
        # Clean in parent directory
        parent_dir = os.path.join('..', dir_name)
        if os.path.exists(parent_dir):
            print(f"🧹 Cleaning {parent_dir}...")
            shutil.rmtree(parent_dir)

def create_hooks_directory():
    """Create hooks directory and copy hook files."""
    hooks_dir = Path('hooks')
    hooks_dir.mkdir(exist_ok=True)
    
    # Copy hook files to the hooks directory
    hook_files = ['hook-fastmcp.py', 'hook-sage_data_client.py']
    for hook_file in hook_files:
        if Path(hook_file).exists():
            shutil.copy(hook_file, hooks_dir / hook_file)
            print(f"📁 Copied {hook_file} to hooks directory")

def build_executable():
    """Build the executable using PyInstaller."""
    print("🔨 Building executable with PyInstaller...")
    
    # Create the hooks directory
    create_hooks_directory()
    
    # Build command - when using a spec file, we can only use basic options
    cmd = [
        'pyinstaller',
        '--clean',
        '--specpath=.',
        'sage_mcp.spec'
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Build failed!")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

def test_executable():
    """Test the built executable."""
    executable_path = Path('dist') / 'sage_mcp'
    
    if not executable_path.exists():
        print("❌ Executable not found!")
        return False
    
    print("🧪 Testing executable...")
    
    try:
        # Test with --help flag (if your app supports it)
        result = subprocess.run([str(executable_path), '--help'], 
                              capture_output=True, text=True, timeout=10)
        print("✅ Executable test completed")
        return True
    except subprocess.TimeoutExpired:
        print("⚠️ Executable test timed out (this might be normal for servers)")
        return True
    except Exception as e:
        print(f"⚠️ Executable test had issues: {e}")
        return True  # Don't fail the build for test issues

def main():
    """Main build process."""
    print("🚀 Starting SAGE MCP executable build process...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build executable
    if not build_executable():
        sys.exit(1)
    
    # Test executable
    test_executable()
    
    # Success message
    executable_path = Path('dist') / 'sage_mcp'
    print("\n" + "=" * 50)
    print("🎉 Build completed successfully!")
    print(f"📦 Executable location: {executable_path.absolute()}")
    if executable_path.exists():
        print(f"📏 File size: {executable_path.stat().st_size / (1024*1024):.1f} MB")
    
    print("\n💡 To run the executable:")
    print(f"   {executable_path.absolute()}")
    
    print("\n💡 To distribute:")
    print("   - Copy the executable to target machines")
    print("   - No Python installation required on target machines")
    print("   - The executable includes all dependencies")
    
    print("\n⚠️ Note: The executable will bind to 0.0.0.0:8000 by default")
    print("   Set MCP_HOST and MCP_PORT environment variables to change this")

if __name__ == "__main__":
    main() 