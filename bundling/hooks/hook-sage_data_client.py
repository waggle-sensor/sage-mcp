#!/usr/bin/env python3
"""
PyInstaller hook for sage_data_client package.
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

# Collect all sage_data_client submodules
hiddenimports = collect_submodules('sage_data_client')

# Collect sage_data_client metadata
try:
    datas = copy_metadata('sage-data-client')
except:
    datas = []

# Collect any data files from sage_data_client
try:
    datas += collect_data_files('sage_data_client')
except:
    pass 