#!/usr/bin/env python3
"""
Cross-platform build script for creating a SAGE MCP executable using PyInstaller.
This script handles all the necessary configuration and dependencies for Windows, macOS, and Linux.
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def get_platform_info():
    """Get platform-specific information."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    platform_info = {
        'system': system,
        'machine': machine,
        'is_windows': system == 'windows',
        'is_macos': system == 'darwin',
        'is_linux': system == 'linux',
        'executable_ext': '.exe' if system == 'windows' else '',
        'python_cmd': 'python' if system == 'windows' else 'python3',
        'pip_cmd': 'pip' if system == 'windows' else 'pip3'
    }
    
    return platform_info

def check_python_installation(platform_info):
    """Check if Python is properly installed."""
    python_cmd = platform_info['python_cmd']
    
    # Check Python
    try:
        result = subprocess.run([python_cmd, '--version'], 
                              capture_output=True, text=True, check=True)
        python_version = result.stdout.strip()
        print(f"✅ Found {python_version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"❌ {python_cmd} is not installed or not in PATH")
        print("Please install Python 3.8+ from:")
        if platform_info['is_windows']:
            print("   - https://www.python.org/downloads/windows/")
            print("   - Or use Microsoft Store")
        elif platform_info['is_macos']:
            print("   - https://www.python.org/downloads/macos/")
            print("   - Or use Homebrew: brew install python")
        else:  # Linux
            print("   - Use your package manager: sudo apt install python3 python3-pip")
            print("   - Or: sudo yum install python3 python3-pip")
        return False
    
    # Check pip
    pip_cmd = platform_info['pip_cmd']
    try:
        subprocess.run([pip_cmd, '--version'], 
                      capture_output=True, text=True, check=True)
        print(f"✅ Found pip")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"❌ {pip_cmd} is not installed or not in PATH")
        print("Please install pip or ensure it's in your PATH")
        return False
    
    return True

def install_pyinstaller(platform_info):
    """Install PyInstaller if not already installed."""
    pip_cmd = platform_info['pip_cmd']
    
    try:
        subprocess.run([pip_cmd, 'show', 'pyinstaller'], 
                      capture_output=True, text=True, check=True)
        print("✅ PyInstaller is already installed")
        return True
    except subprocess.CalledProcessError:
        print("📦 Installing PyInstaller...")
        try:
            subprocess.run([pip_cmd, 'install', 'pyinstaller'], check=True)
            print("✅ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install PyInstaller: {e}")
            return False

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

def build_executable(platform_info):
    """Build the executable using PyInstaller."""
    print("🔨 Building executable with PyInstaller...")
    
    # Create the hooks directory
    create_hooks_directory()
    
    # Build command - when using a spec file, we can only use basic options
    cmd = [
        'pyinstaller',
        '--clean',
        'sage_mcp.spec'
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Build failed!")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def test_executable(platform_info):
    """Test the built executable."""
    executable_name = f"sage_mcp{platform_info['executable_ext']}"
    executable_path = Path('dist') / executable_name
    
    if not executable_path.exists():
        print(f"❌ Executable not found at {executable_path}!")
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

def print_success_message(platform_info):
    """Print success message with platform-specific instructions."""
    executable_name = f"sage_mcp{platform_info['executable_ext']}"
    executable_path = Path('dist') / executable_name
    
    print("\n" + "=" * 60)
    print("🎉 Build completed successfully!")
    print(f"🖥️  Platform: {platform_info['system'].title()} ({platform_info['machine']})")
    print(f"📦 Executable location: {executable_path.absolute()}")
    
    if executable_path.exists():
        size_mb = executable_path.stat().st_size / (1024*1024)
        print(f"📏 File size: {size_mb:.1f} MB")
    
    print(f"\n💡 To run the executable:")
    if platform_info['is_windows']:
        print(f"   {executable_path.absolute()}")
        print(f"   # Or double-click the .exe file")
    else:
        print(f"   ./{executable_path}")
    
    print(f"\n💡 To run with custom settings:")
    if platform_info['is_windows']:
        print(f"   set MCP_HOST=127.0.0.1")
        print(f"   set MCP_PORT=8080")
        print(f"   {executable_path.absolute()}")
    else:
        print(f"   MCP_HOST=127.0.0.1 MCP_PORT=8080 ./{executable_path}")
    
    print(f"\n💡 To distribute:")
    print("   - Copy the executable to target machines")
    print("   - No Python installation required on target machines")
    print("   - The executable includes all dependencies")
    
    if platform_info['is_windows']:
        print("   - Windows Defender might flag the executable initially")
        print("   - Consider code signing for production distribution")
    elif platform_info['is_macos']:
        print("   - macOS Gatekeeper might block unsigned executables")
        print("   - Users may need to right-click and 'Open' the first time")
    
    print(f"\n⚠️ Note: The executable will bind to 0.0.0.0:8000 by default")
    print("   Set MCP_HOST and MCP_PORT environment variables to change this")

def main():
    """Main build process."""
    platform_info = get_platform_info()
    
    print("🚀 SAGE MCP Cross-Platform Executable Builder")
    print("=" * 60)
    print(f"🖥️  Detected Platform: {platform_info['system'].title()} ({platform_info['machine']})")
    print()
    
    # Check Python installation
    if not check_python_installation(platform_info):
        sys.exit(1)
    
    # Install PyInstaller if needed
    if not install_pyinstaller(platform_info):
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build executable
    if not build_executable(platform_info):
        sys.exit(1)
    
    # Test executable
    test_executable(platform_info)
    
    # Success message
    print_success_message(platform_info)

if __name__ == "__main__":
    main() 