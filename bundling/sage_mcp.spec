# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from pathlib import Path

# Get the parent directory (where sage_mcp.py is located)
import os
current_dir = Path(os.getcwd()).parent

block_cipher = None

# Define additional data files that need to be included
datas = []

# Include package metadata for packages that PyInstaller might miss
# This fixes the "No package metadata was found" errors
hidden_imports = [
    'fastmcp',
    'mcp',
    'sage_data_client',
    'pandas',
    'numpy',
    'pydantic',
    'yaml',
    'requests',
    'httpx',
    'asyncio',
    'logging',
    'json',
    'datetime',
    'pathlib',
    'tempfile',
    'subprocess',
    'enum',
    'typing',
    're',
    'os',
    'sys',
    # Include all the sage_mcp_server modules
    'sage_mcp_server',
    'sage_mcp_server.models',
    'sage_mcp_server.utils',
    'sage_mcp_server.data_service',
    'sage_mcp_server.job_service',
    'sage_mcp_server.docs_helper',
    'sage_mcp_server.plugin_generator',
    'sage_mcp_server.plugin_metadata',
    'sage_mcp_server.plugin_query_service',
    'sage_mcp_server.plugin_registry',
    'sage_mcp_server.job_templates',
    # Additional imports that might be needed
    'asyncio_mqtt',
    'uvicorn',
    'starlette',
    'fastapi',
]

# Try to collect package metadata using PyInstaller utilities
try:
    from PyInstaller.utils.hooks import copy_metadata, collect_data_files
    
    # Packages that need metadata
    packages_needing_metadata = [
        'fastmcp', 'mcp', 'sage-data-client', 'pandas', 'numpy', 
        'pydantic', 'pyyaml', 'requests', 'httpx'
    ]
    
    for package in packages_needing_metadata:
        try:
            # Use PyInstaller's copy_metadata function
            metadata_files = copy_metadata(package)
            if metadata_files:
                datas.extend(metadata_files)
                print(f"✅ Collected metadata for {package}")
        except Exception as e:
            print(f"Warning: Could not collect metadata for {package}: {e}")
            # Try alternative package name (replace hyphens with underscores)
            alt_package = package.replace('-', '_')
            try:
                metadata_files = copy_metadata(alt_package)
                if metadata_files:
                    datas.extend(metadata_files)
                    print(f"✅ Collected metadata for {alt_package} (alternative name)")
            except Exception as e2:
                print(f"Warning: Could not collect metadata for {alt_package} either: {e2}")
            
except ImportError:
    print("Warning: Could not import PyInstaller metadata collection utilities")

# Include the entire sage_mcp_server package
sage_server_path = current_dir / 'sage_mcp_server'
if sage_server_path.exists():
    datas.append((str(sage_server_path), 'sage_mcp_server'))

a = Analysis(
    [str(current_dir / 'sage_mcp.py')],
    pathex=[str(current_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[str(Path.cwd() / 'hooks')],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude some heavy packages we don't need
        'matplotlib',
        'scipy',
        'jupyter',
        'notebook',
        'tkinter',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove duplicate entries
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='sage_mcp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Set icon if you have one
    # icon='sage_icon.ico',
) 