from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Union
from enum import Enum
import re
import logging
from datetime import datetime, timedelta
import pandas as pd
import requests

logger = logging.getLogger(__name__)

# Data Models
class DataCategory(str, Enum):
    """Categories of data that plugins can provide"""
    ENVIRONMENTAL = "environmental"
    CAMERA = "camera"
    RAIN = "rain"
    MOTION = "motion"
    AUDIO = "audio"
    NETWORK = "network"
    SYSTEM = "system"
    OTHER = "other"

@dataclass
class MeasurementType:
    """Model for a specific type of measurement"""
    name: str  # e.g. "env.temperature"
    category: DataCategory
    unit: Optional[str] = None  # e.g. "°C"
    description: Optional[str] = None
    plugin_patterns: List[str] = None  # List of regex patterns to match plugin names

    def __post_init__(self):
        if self.plugin_patterns is None:
            self.plugin_patterns = []

@dataclass
class Plugin:
    """Model for a SAGE plugin"""
    name: str  # e.g. "waggle/plugin-iio:0.4.1"
    version: str
    measurements: List[MeasurementType]
    description: Optional[str] = None
    capabilities: Set[str] = None

    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = set()

class PluginRegistry:
    """Registry for managing plugin metadata and search"""
    
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.measurements: Dict[str, MeasurementType] = {}
        self._initialize_known_measurements()
        self._initialize_known_plugins()
        self.refresh_cache()
    
    def refresh_cache(self) -> None:
        """Refresh the plugin metadata cache from the SAGE API"""
        try:
            response = requests.get(SAGE_PLUGINS_URL, timeout=10)
            if response.status_code == 200:
                plugins_data = response.json()
                for plugin_data in plugins_data:
                    try:
                        plugin = Plugin(
                            name=plugin_data.get("name", ""),
                            version=plugin_data.get("version", "0.0.0"),
                            measurements=[],
                            description=plugin_data.get("description", ""),
                            capabilities=set()
                        )
                        if plugin.name:  # Only add if we have a valid name
                            self.plugins[plugin.name] = plugin
                    except Exception as e:
                        logger.warning(f"Error parsing plugin data: {e}")
                logger.info(f"Cached {len(self.plugins)} plugins")
            else:
                logger.error(f"Failed to fetch plugins: {response.status_code}")
        except Exception as e:
            logger.error(f"Error refreshing plugin cache: {e}")
            # Ensure we have at least the known plugins
            self._initialize_known_plugins()

    def _initialize_known_measurements(self) -> None:
        """Initialize known measurement types"""
        measurements = [
            MeasurementType(
                name="env.temperature",
                category=DataCategory.ENVIRONMENTAL,
                unit="°C",
                description="Environmental temperature",
                plugin_patterns=[".*plugin-iio.*", ".*plugin-bme680.*"]
            ),
            MeasurementType(
                name="env.relative_humidity",
                category=DataCategory.ENVIRONMENTAL,
                unit="%",
                description="Relative humidity",
                plugin_patterns=[".*plugin-iio.*", ".*plugin-bme680.*"]
            ),
            MeasurementType(
                name="env.pressure",
                category=DataCategory.ENVIRONMENTAL,
                unit="Pa",
                description="Atmospheric pressure",
                plugin_patterns=[".*plugin-iio.*", ".*plugin-bme680.*"]
            ),
            MeasurementType(
                name="env.raingauge.rint",
                category=DataCategory.RAIN,
                unit="mm/hr",
                description="Rain intensity (past minute, extrapolated to hour)",
                plugin_patterns=[".*plugin-raingauge.*"]
            ),
            MeasurementType(
                name="env.raingauge.event_acc",
                category=DataCategory.RAIN,
                unit="mm",
                description="Rain event accumulation",
                plugin_patterns=[".*plugin-raingauge.*"]
            ),
            # Add more measurement types as needed
        ]

        for measurement in measurements:
            self.measurements[measurement.name] = measurement

    def _initialize_known_plugins(self) -> None:
        """Initialize known plugins"""
        plugins = [
            Plugin(
                name="waggle/plugin-iio",
                version="0.4.1",
                description="Industrial I/O sensor plugin",
                measurements=[
                    self.measurements["env.temperature"],
                    self.measurements["env.relative_humidity"],
                    self.measurements["env.pressure"]
                ]
            ),
            Plugin(
                name="waggle/plugin-raingauge",
                version="0.4.1",
                description="Rain gauge plugin",
                measurements=[
                    self.measurements["env.raingauge.rint"],
                    self.measurements["env.raingauge.event_acc"]
                ]
            ),
            # Add more plugins as needed
        ]

        for plugin in plugins:
            self.plugins[plugin.name] = plugin

    def get_plugins_for_measurement(self, measurement_name: str) -> List[Plugin]:
        """Get all plugins that can provide a specific measurement"""
        matching_plugins = []
        measurement = self.measurements.get(measurement_name)
        
        if not measurement:
            return []

        for plugin in self.plugins.values():
            if any(m.name == measurement_name for m in plugin.measurements):
                matching_plugins.append(plugin)

        return matching_plugins

    def get_measurement_info(self, measurement_name: str) -> Optional[MeasurementType]:
        """Get information about a specific measurement type"""
        return self.measurements.get(measurement_name)

    def get_plugins_by_category(self, category: DataCategory) -> List[Plugin]:
        """Get all plugins that provide measurements in a specific category"""
        matching_plugins = []
        
        for plugin in self.plugins.values():
            if any(m.category == category for m in plugin.measurements):
                matching_plugins.append(plugin)

        return matching_plugins

    def get_measurements_by_category(self, category: DataCategory) -> List[MeasurementType]:
        """Get all measurements in a specific category"""
        return [m for m in self.measurements.values() if m.category == category]

    def register_plugin(self, plugin: Plugin) -> None:
        """Register a new plugin"""
        self.plugins[plugin.name] = plugin
        logger.info(f"Registered plugin: {plugin.name}")

    def register_measurement(self, measurement: MeasurementType) -> None:
        """Register a new measurement type"""
        self.measurements[measurement.name] = measurement
        logger.info(f"Registered measurement type: {measurement.name}")

class QueryBuilder:
    """Helper class to build SAGE data queries"""
    
    def __init__(self, registry: PluginRegistry):
        self.registry = registry

    def build_query_params(
        self,
        measurement_name: str,
        node_id: Optional[str] = None,
        time_range: str = "-30m"
    ) -> Dict[str, str]:
        """Build query parameters for a specific measurement"""
        params = {"name": measurement_name}
        
        if node_id:
            params["vsn"] = node_id

        measurement = self.registry.get_measurement_info(measurement_name)
        if not measurement:
            return params

        # If measurement has specific plugin patterns, add them to query
        if measurement.plugin_patterns:
            # Use first plugin pattern as primary filter
            params["plugin"] = measurement.plugin_patterns[0]

        return params

    def build_category_query(
        self,
        category: DataCategory,
        node_id: Optional[str] = None,
        time_range: str = "-30m"
    ) -> Dict[str, str]:
        """Build query parameters for all measurements in a category"""
        measurements = self.registry.get_measurements_by_category(category)
        if not measurements:
            return {}

        # Create name filter with all measurement names
        name_filter = "|".join(m.name for m in measurements)
        params = {"name": name_filter}

        if node_id:
            params["vsn"] = node_id

        return params 