#!/usr/bin/env python3

import logging
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

from plugin_registry import (
    PluginRegistry,
    DataCategory,
    MeasurementType,
    Plugin
)
from plugin_data_service import PluginDataService, DataQueryResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
registry = PluginRegistry()
data_service = PluginDataService(registry)

# Initialize MCP
mcp = FastMCP("SagePluginMCP")

def format_query_result(result: DataQueryResult) -> str:
    """Format a query result for display"""
    if result.error:
        return f"❌ Error: {result.error}"

    if result.is_empty:
        return "No data found for the specified criteria."

    # Build response
    response = []
    
    # Add measurement info header
    if result.measurement:
        response.append(f"📊 {result.measurement.name}")
        if result.measurement.description:
            response.append(f"Description: {result.measurement.description}")
        if result.measurement.unit:
            response.append(f"Unit: {result.measurement.unit}")
    
    # Add data summary
    response.append(f"\nFound {result.row_count} readings from {len(result.data['meta.vsn'].unique())} nodes")
    
    # Add time range
    if not result.data.empty:
        time_start = result.data['timestamp'].min()
        time_end = result.data['timestamp'].max()
        response.append(f"Time range: {time_start} to {time_end}")
    
    # Add value summary
    if 'value' in result.data.columns:
        response.append("\nValue Summary:")
        response.append(f"  Min: {result.data['value'].min():.2f}")
        response.append(f"  Max: {result.data['value'].max():.2f}")
        response.append(f"  Mean: {result.data['value'].mean():.2f}")
    
    return "\n".join(response)

# ----------------------------------------
# MCP Tools
# ----------------------------------------

@mcp.tool()
def query_measurement_data(
    measurement_name: str,
    node_id: str = "",
    time_range: str = "-30m",
    filter_expr: str = ""
) -> str:
    """Query data for a specific measurement type"""
    try:
        result = data_service.query_measurement(
            measurement_name=measurement_name,
            node_id=node_id if node_id else None,
            time_range=time_range,
            filter_expr=filter_expr if filter_expr else None
        )
        return format_query_result(result)
    except Exception as e:
        logger.error(f"Error in query_measurement_data: {e}")
        return f"Error querying measurement data: {str(e)}"

@mcp.tool()
def query_category_data(
    category: str,
    node_id: str = "",
    time_range: str = "-30m",
    filter_expr: str = ""
) -> str:
    """Query all measurements in a category"""
    try:
        # Convert string to DataCategory
        try:
            data_category = DataCategory(category.lower())
        except ValueError:
            return f"Invalid category: {category}. Valid categories are: {', '.join(c.value for c in DataCategory)}"

        results = data_service.query_category(
            category=data_category,
            node_id=node_id if node_id else None,
            time_range=time_range,
            filter_expr=filter_expr if filter_expr else None
        )

        if not results:
            return f"No measurements found in category: {category}"

        # Combine results
        response = [f"📊 {category.upper()} Data Summary"]
        for result in results:
            response.append("\n" + "="*40 + "\n")
            response.append(format_query_result(result))

        return "\n".join(response)
    except Exception as e:
        logger.error(f"Error in query_category_data: {e}")
        return f"Error querying category data: {str(e)}"

@mcp.tool()
def get_latest_measurement_values(
    measurement_name: str,
    node_id: str = ""
) -> str:
    """Get latest values for a measurement"""
    try:
        result = data_service.get_latest_values(
            measurement_name=measurement_name,
            node_id=node_id if node_id else None
        )

        if result.error:
            return f"❌ Error: {result.error}"

        if result.is_empty:
            return f"No recent data found for {measurement_name}"

        # Format response
        response = [f"📊 Latest {measurement_name} Values"]
        if result.measurement and result.measurement.unit:
            response[0] += f" ({result.measurement.unit})"

        for _, row in result.data.iterrows():
            node = row.get('meta.vsn', 'Unknown')
            value = row.get('value', 'N/A')
            timestamp = row.get('timestamp', 'Unknown time')
            response.append(f"\nNode {node}: {value:.2f} @ {timestamp}")

        return "\n".join(response)
    except Exception as e:
        logger.error(f"Error in get_latest_measurement_values: {e}")
        return f"Error getting latest values: {str(e)}"

@mcp.tool()
def get_measurement_statistics(
    measurement_name: str,
    node_id: str = "",
    time_range: str = "-1h",
    filter_expr: str = ""
) -> str:
    """Get statistics for a measurement"""
    try:
        stats = data_service.get_measurement_stats(
            measurement_name=measurement_name,
            node_id=node_id if node_id else None,
            time_range=time_range,
            filter_expr=filter_expr if filter_expr else None
        )

        if stats.get('error'):
            return f"❌ Error: {stats['error']}"

        if not stats.get('stats'):
            return f"No data found for {measurement_name}"

        # Format response
        response = [f"📊 Statistics for {measurement_name}"]
        if stats.get('unit'):
            response[0] += f" ({stats['unit']})"

        stat_data = stats['stats']
        response.extend([
            f"\nTime Range: {stat_data['time_range']['start']} to {stat_data['time_range']['end']}",
            f"Total Readings: {stat_data['count']}",
            f"Unique Nodes: {stat_data['nodes']}",
            f"\nValue Statistics:",
            f"  Mean: {stat_data['mean']:.2f}",
            f"  Min: {stat_data['min']:.2f}",
            f"  Max: {stat_data['max']:.2f}",
            f"  Std Dev: {stat_data['std']:.2f}"
        ])

        return "\n".join(response)
    except Exception as e:
        logger.error(f"Error in get_measurement_statistics: {e}")
        return f"Error getting statistics: {str(e)}"

@mcp.tool()
def list_available_measurements(category: str = "") -> str:
    """List all available measurements, optionally filtered by category"""
    try:
        if category:
            try:
                data_category = DataCategory(category.lower())
                measurements = registry.get_measurements_by_category(data_category)
                response = [f"📊 Available {category.upper()} Measurements:"]
            except ValueError:
                return f"Invalid category: {category}. Valid categories are: {', '.join(c.value for c in DataCategory)}"
        else:
            measurements = list(registry.measurements.values())
            response = ["📊 All Available Measurements:"]

        if not measurements:
            return "No measurements found."

        # Group by category
        by_category: Dict[str, List[MeasurementType]] = {}
        for m in measurements:
            if m.category.value not in by_category:
                by_category[m.category.value] = []
            by_category[m.category.value].append(m)

        # Format response
        for cat, cat_measurements in sorted(by_category.items()):
            response.append(f"\n{cat.upper()}:")
            for m in sorted(cat_measurements, key=lambda x: x.name):
                response.append(f"  - {m.name}")
                if m.unit:
                    response[-1] += f" ({m.unit})"
                if m.description:
                    response.append(f"    {m.description}")

        return "\n".join(response)
    except Exception as e:
        logger.error(f"Error in list_available_measurements: {e}")
        return f"Error listing measurements: {str(e)}"

# ----------------------------------------
# Server Entry Point
# ----------------------------------------

def main() -> None:
    """Main entry point"""
    try:
        logger.info("Starting SagePluginMCP server...")
        mcp.run(transport="streamable-http")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    main() 