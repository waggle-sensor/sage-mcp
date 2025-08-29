"""
Sage MCP Server Package

This package contains the core components for the Sage MCP (Model Context Protocol) server.
"""

# Core data models
from .models import (
    SageConfig, TimeRange, NodeID, DataType, SelectorRequirements,
    PluginArguments, PluginSpec, SageJob, CameraSageJob
)

# Utility functions
from .utils import safe_timestamp_format, parse_time_range

# Core services
from .data_service import SageDataService
from .job_service import SageJobService
from .docs_helper import SAGEDocsHelper

# Plugin system
from .plugin_metadata import plugin_registry
from .plugin_query_service import plugin_query_service
from .plugin_generator import PluginTemplate, PluginRequirements, PluginGenerator

# Job templates
from .job_templates import JobTemplates

__version__ = "1.0.0"
__all__ = [
    # Models
    "SageConfig", "TimeRange", "NodeID", "DataType", "SelectorRequirements",
    "PluginArguments", "PluginSpec", "SageJob", "CameraSageJob",
    # Utils
    "safe_timestamp_format", "parse_time_range",
    # Services
    "SageDataService", "SageJobService", "SAGEDocsHelper",
    # Plugin system
    "plugin_registry", "plugin_query_service", "PluginTemplate",
    "PluginRequirements", "PluginGenerator",
    # Templates
    "JobTemplates",
]