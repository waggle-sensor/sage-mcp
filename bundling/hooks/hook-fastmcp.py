#!/usr/bin/env python3
"""
PyInstaller hook for fastmcp package.
This ensures that fastmcp and its metadata are properly included in the executable.
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

# Collect all fastmcp submodules
hiddenimports = collect_submodules('fastmcp')

# Collect fastmcp metadata
datas = copy_metadata('fastmcp')

# Collect any data files from fastmcp
datas += collect_data_files('fastmcp')

# Also collect MCP metadata since fastmcp depends on it
try:
    datas += copy_metadata('mcp')
    hiddenimports += collect_submodules('mcp')
except:
    pass 