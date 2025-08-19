from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
import pandas as pd
import re
import os

from .plugin_metadata import plugin_registry, PluginMetadata
import sage_data_client

logger = logging.getLogger(__name__)

class PluginQueryService:
    """Service for handling natural language queries about plugins and their data"""
    
    def __init__(self):
        self.registry = plugin_registry
        
        # Common plugin categories and their keywords
        self.categories = {
            "cloud": ["cloud", "sky", "weather", "atmospheric", "cover"],
            "image": ["image", "camera", "sampling", "capture", "photo", "picture"],
            "vehicle": ["car", "vehicle", "traffic", "detection", "counting"],
            "people": ["person", "pedestrian", "crowd", "detection", "human"],
            "temperature": ["temperature", "environmental", "weather", "temp"],
            "rain": ["rain", "precipitation", "weather", "rainfall", "gauge"],
            "motion": ["motion", "movement", "tracking", "speed", "velocity"],
            "audio": ["sound", "noise", "audio", "acoustic", "microphone"],
            "air": ["air", "quality", "pollution", "particulate", "gas"],
        }
        
        # Common data types and their patterns
        self.data_patterns = {
            "cloud_cover": r".*cloud.*cover.*",
            "cloud_motion": r".*cloud.*motion.*",
            "image_sampler": r".*imagesampler.*",
            "rain_gauge": r".*raingauge.*",
            "air_quality": r".*air.*quality.*",
            "temperature": r".*temperature.*",
            "motion": r".*motion.*",
            "audio": r".*audio.*",
        }
    
    def parse_natural_query(self, query: str) -> Dict[str, Any]:
        """Parse a natural language query into structured parameters"""
        query = query.lower()
        params = {}

        # Initialize categories list
        categories = []

        # Handle PTZ-YOLO specific queries
        if any(term in query for term in ["ptz", "pan", "tilt", "zoom"]):
            if "yolo" in query or "detect" in query or "recognition" in query:
                params["plugin_pattern"] = ".*ptzapp-yolo.*"
                categories.append("camera")
            else:
                params["plugin_pattern"] = ".*ptz.*"
                categories.append("camera")

        # Handle image and camera related queries
        elif any(term in query for term in ["image", "camera", "photo", "picture"]):
            if "yolo" in query or "detect" in query or "recognition" in query:
                params["plugin_pattern"] = ".*yolo.*"
                categories.append("camera")
            else:
                params["plugin_pattern"] = ".*imagesampler.*|.*camera.*"
                categories.append("camera")

        # Handle environmental queries
        elif any(term in query for term in ["temperature", "humidity", "pressure", "weather", "environmental"]):
            categories.append("environmental")

        # Handle audio queries
        elif any(term in query for term in ["audio", "sound", "microphone", "recording"]):
            categories.append("audio")

        # Handle cloud/rain queries
        elif any(term in query for term in ["cloud", "rain", "precipitation", "sky"]):
            categories.append("rain")

        # Add categories to params if any were found
        if categories:
            params["categories"] = categories

        # Extract time range if specified
        time_matches = re.findall(r"(\d+)\s*(hour|hr|minute|min)s?(?:\s+ago)?", query)
        if time_matches:
            amount, unit = time_matches[0]
            if unit.startswith("hour"):
                params["time_range"] = f"-{amount}h"
            elif unit.startswith("min"):
                params["time_range"] = f"-{amount}m"

        # Set default values if not specified
        if "time_range" not in params:
            params["time_range"] = "-1h"
        
        # Set nodes to None (will query all nodes)
        params["nodes"] = None

        return params
    
    def find_plugins_for_task(self, task_description: str) -> List[PluginMetadata]:
        """Find plugins suitable for a given task description"""
        # Parse the natural language query
        params = self.parse_natural_query(task_description)
        
        # Search for matching plugins
        matching_plugins = []
        
        # Search by categories if specified
        if "categories" in params:
            for category in params["categories"]:
                plugins = self.registry.get_plugins_by_type(category)
                matching_plugins.extend(plugins)
        
        # Search by direct plugin name/description
        direct_matches = self.registry.search_plugins(task_description)
        matching_plugins.extend(direct_matches)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_plugins = []
        for plugin in matching_plugins:
            if plugin.id not in seen:
                seen.add(plugin.id)
                unique_plugins.append(plugin)
        
        return unique_plugins
    
    def query_plugin_data(
        self,
        plugin_id: str,
        nodes: Optional[List[str]] = None,
        time_range: str = "-1h",
        start: str = None,
        end: str = None,
        user_token: Optional[str] = None,
        **kwargs
    ) -> pd.DataFrame:
        """Query data produced by a specific plugin"""
        plugin = self.registry.get_plugin_by_id(plugin_id)
        if not plugin:
            logger.error(f"Plugin not found: {plugin_id}")
            return pd.DataFrame()
        # Use provided start/end or parse from time_range
        if not start:
            if 'T' in time_range and 'Z' in time_range:
                try:
                    start_time = datetime.strptime(time_range, '%Y-%m-%dT%H:%M:%SZ')
                    end_time = start_time + timedelta(hours=1)
                    start = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
                    end = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
                except Exception:
                    start = time_range
                    end = None
            else:
                match = re.match(r'-(\d+)([hm])', time_range)
                now = datetime.utcnow()
                if match:
                    amount = int(match.group(1))
                    unit = match.group(2)
                    if unit == 'h':
                        delta = timedelta(hours=amount)
                    else:
                        delta = timedelta(minutes=amount)
                    start = (now - delta).strftime('%Y-%m-%dT%H:%M:%SZ')
                    end = now.strftime('%Y-%m-%dT%H:%M:%SZ')
                else:
                    start = time_range
                    end = None
        filter_params = {"plugin": f".*{plugin.name}.*"}
        if nodes:
            filter_params["vsn"] = "|".join(nodes)
        else:
            filter_params["vsn"] = "*"
        try:
            query_args = {"start": start, "filter": filter_params}
            if end:
                query_args["end"] = end
            # Note: sage_data_client.query() does not accept authentication parameters
            # Authentication for protected data must be configured at the system level
            if user_token:
                if ':' in user_token:
                    username, _ = user_token.split(':', 1)
                    logger.info(f"User token provided (username: {username}) - attempting plugin query")
                    logger.warning("sage_data_client authentication not yet implemented - may only return public data")
                else:
                    logger.warning(f"Token provided without username. For protected data access, use 'username:token' format")
                    logger.info(f"Querying plugin {plugin.name} with simple token - may only return public data")
            else:
                logger.info(f"Querying plugin {plugin.name} without authentication")
            
            df = sage_data_client.query(**query_args)
            if df.empty:
                logger.warning(f"No data found for plugin {plugin.name}")
            else:
                logger.info(f"Found {len(df)} records for plugin {plugin.name}")
            return df
        except Exception as e:
            logger.error(f"Error querying plugin data: {e}")
            return pd.DataFrame()
    
    def format_plugin_data(self, df: pd.DataFrame, plugin: PluginMetadata) -> str:
        """Format plugin data results in a user-friendly way"""
        if df.empty:
            return f"No data found for plugin {plugin.name}"
        
        result = [f"📊 Data from {plugin.name}:"]
        result.append(f"Total records: {len(df)}")
        
        if 'timestamp' in df.columns:
            latest = df['timestamp'].max()
            earliest = df['timestamp'].min()
            result.append(f"Time range: {earliest} to {latest}")
        
        if 'meta.vsn' in df.columns:
            nodes = sorted(df['meta.vsn'].unique())
            result.append(f"Nodes: {', '.join(nodes)}")
        
        # Add value statistics if available
        if 'value' in df.columns:
            try:
                # Try to convert to numeric and calculate statistics
                numeric_values = pd.to_numeric(df['value'], errors='coerce')
                if not numeric_values.isna().all():
                    result.append("\nValue Statistics:")
                    result.append(f"  Minimum: {numeric_values.min():.2f}")
                    result.append(f"  Maximum: {numeric_values.max():.2f}")
                    result.append(f"  Average: {numeric_values.mean():.2f}")
                else:
                    result.append(f"\nValue types: {df['value'].dtype}")
            except Exception as e:
                logger.warning(f"Could not calculate value statistics: {e}")
                result.append(f"\nValue column present ({len(df)} records)")
        
        # Add plugin description if available
        if plugin.description:
            result.append(f"\nPlugin Description: {plugin.description}")
        
        # Add science description if available
        if plugin.science_description:
            result.append(f"Science Description: {plugin.science_description}")
        
        return "\n".join(result)
    
    def query_by_natural_language(self, query: str, user_token: Optional[str] = None) -> str:
        """Handle a natural language query about plugin data"""
        try:
            # Parse the query
            params = self.parse_natural_query(query)
            
            # Find relevant plugins
            plugins = self.find_plugins_for_task(query)
            
            if not plugins:
                return "No plugins found matching your query. Try using different keywords or be more specific."
            
            results = []
            for plugin in plugins:
                # Query data for each plugin
                df = self.query_plugin_data(
                    plugin_id=plugin.id,
                    nodes=params["nodes"],
                    time_range=params["time_range"],
                    user_token=user_token
                )
                
                # Format and add results
                plugin_result = self.format_plugin_data(df, plugin)
                results.append(plugin_result)
            
            # Combine all results
            return "\n\n" + "\n\n".join(results)
            
        except Exception as e:
            logger.error(f"Error processing natural language query: {e}")
            return f"Error processing your query: {str(e)}"

# Initialize global service
plugin_query_service = PluginQueryService() 