# Adding Custom Functions to SAGE MCP Server

This guide explains how to fork the SAGE MCP server repository and add your own custom MCP tools and functions.

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Basic Custom Function](#basic-custom-function)
- [Advanced Examples](#advanced-examples)
- [Best Practices](#best-practices)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## Overview

The SAGE MCP server is built using [FastMCP](https://github.com/jlowin/fastmcp), which makes it easy to add custom Model Context Protocol (MCP) tools. You can extend the server with:

- **Custom data analysis functions**
- **Specialized sensor data processing**
- **Integration with external APIs**
- **Custom visualization tools**
- **Domain-specific research tools**

## Getting Started

### 1. Fork the Repository

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/sage-mcp.git
cd sage-mcp

# Add the upstream remote to stay updated
git remote add upstream https://github.com/sagecontinuum/sage-mcp.git
```

### 2. Set Up Development Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Test that everything works
python test_dependencies.py
python sage_mcp.py
```

### 3. Understanding the Structure

The main server code is in `sage_mcp.py`. Key components:

```python
# Server initialization
mcp = FastMCP("SageDataMCP")

# Tool definition
@mcp.tool()
def your_function_name(param1: str, param2: int = 10) -> str:
    """Function description that appears in MCP clients"""
    # Your implementation
    return "Result"

# Server startup
if __name__ == "__main__":
    main()
```

## Basic Custom Function

Here's a simple example of adding a custom function:

### Example 1: Custom Temperature Analysis

Add this function anywhere in `sage_mcp.py` before the `main()` function:

```python
@mcp.tool()
def analyze_temperature_trends(
    node_id: str, 
    days: int = 7,
    threshold_temp: float = 25.0
) -> str:
    """
    Analyze temperature trends for a node over specified days.
    
    Args:
        node_id: SAGE node identifier (e.g., 'W023')
        days: Number of days to analyze (default: 7)
        threshold_temp: Temperature threshold in Celsius (default: 25.0)
    
    Returns:
        Formatted analysis report
    """
    try:
        # Validate inputs
        validated_node = NodeID(value=node_id)
        
        # Calculate time range
        time_range = f"-{days}d"
        
        # Get data using existing data service
        data_service = SageDataService()
        user_token = get_current_user_token()
        
        # Query temperature data
        temp_data = data_service.query_data(
            start=time_range,
            filter_params={
                "name": "env.temperature",
                "vsn": validated_node.value
            },
            user_token=user_token
        )
        
        if temp_data.empty:
            return f"❌ No temperature data found for node {node_id} in the last {days} days"
        
        # Perform analysis
        avg_temp = temp_data['value'].mean()
        max_temp = temp_data['value'].max()
        min_temp = temp_data['value'].min()
        
        # Count readings above threshold
        high_temp_count = len(temp_data[temp_data['value'] > threshold_temp])
        total_readings = len(temp_data)
        high_temp_percentage = (high_temp_count / total_readings) * 100
        
        # Format results
        results = [
            f"🌡️ **Temperature Analysis for Node {node_id}**",
            f"",
            f"📊 **Statistics ({days} days):**",
            f"• Average: {avg_temp:.1f}°C",
            f"• Maximum: {max_temp:.1f}°C", 
            f"• Minimum: {min_temp:.1f}°C",
            f"• Total readings: {total_readings}",
            f"",
            f"🔥 **Threshold Analysis (>{threshold_temp}°C):**",
            f"• High temperature readings: {high_temp_count}",
            f"• Percentage above threshold: {high_temp_percentage:.1f}%",
        ]
        
        return "\\n".join(results)
        
    except Exception as e:
        logger.error(f"Error in temperature trend analysis: {e}")
        return f"❌ Error analyzing temperature trends: {str(e)}"
```

### Testing Your Function

```bash
# Start the server
python sage_mcp.py

# Your new function will appear in the list of available tools
# Test it through your MCP client with:
# analyze_temperature_trends("W023", 7, 25.0)
```

## Advanced Examples

### Example 2: Multi-Node Comparison Tool

```python
@mcp.tool()
def compare_nodes_environmental(
    node_ids: str,
    metric: str = "env.temperature", 
    time_range: str = "-24h"
) -> str:
    """
    Compare environmental metrics across multiple nodes.
    
    Args:
        node_ids: Comma-separated list of node IDs (e.g., "W023,W027,W019")
        metric: Environmental metric to compare (default: "env.temperature")
        time_range: Time range for comparison (default: "-24h")
    """
    try:
        # Parse node list
        nodes = [node.strip() for node in node_ids.split(',') if node.strip()]
        if not nodes:
            return "❌ No valid nodes provided"
        
        data_service = SageDataService()
        user_token = get_current_user_token()
        
        results = []
        node_stats = {}
        
        # Collect data for each node
        for node_id in nodes:
            try:
                validated_node = NodeID(value=node_id)
                
                data = data_service.query_data(
                    start=time_range,
                    filter_params={
                        "name": metric,
                        "vsn": validated_node.value
                    },
                    user_token=user_token
                )
                
                if not data.empty:
                    node_stats[node_id] = {
                        'avg': data['value'].mean(),
                        'max': data['value'].max(),
                        'min': data['value'].min(),
                        'count': len(data)
                    }
                else:
                    node_stats[node_id] = None
                    
            except Exception as e:
                logger.warning(f"Error processing node {node_id}: {e}")
                node_stats[node_id] = None
        
        # Format comparison results
        results = [
            f"📊 **Multi-Node Environmental Comparison**",
            f"",
            f"**Metric:** {metric}",
            f"**Time Range:** {time_range}",
            f"**Nodes:** {', '.join(nodes)}",
            f"",
            "| Node | Avg | Max | Min | Readings |",
            "|------|-----|-----|-----|----------|"
        ]
        
        for node_id in nodes:
            stats = node_stats[node_id]
            if stats:
                results.append(
                    f"| {node_id} | {stats['avg']:.1f} | {stats['max']:.1f} | {stats['min']:.1f} | {stats['count']} |"
                )
            else:
                results.append(f"| {node_id} | No data | No data | No data | 0 |")
        
        # Add summary insights
        valid_nodes = {k: v for k, v in node_stats.items() if v is not None}
        if valid_nodes:
            best_avg = min(valid_nodes.items(), key=lambda x: x[1]['avg'])
            worst_avg = max(valid_nodes.items(), key=lambda x: x[1]['avg'])
            
            results.extend([
                f"",
                f"🏆 **Insights:**",
                f"• Lowest average: {best_avg[0]} ({best_avg[1]['avg']:.1f})",
                f"• Highest average: {worst_avg[0]} ({worst_avg[1]['avg']:.1f})"
            ])
        
        return "\\n".join(results)
        
    except Exception as e:
        logger.error(f"Error in multi-node comparison: {e}")
        return f"❌ Error comparing nodes: {str(e)}"
```

### Example 3: Custom Data Export Tool

```python
@mcp.tool()
def export_node_data_csv(
    node_id: str,
    time_range: str = "-24h",
    measurements: str = "env.temperature,env.humidity,env.pressure"
) -> str:
    """
    Export node data to CSV format for external analysis.
    
    Args:
        node_id: SAGE node identifier
        time_range: Time range for data export
        measurements: Comma-separated list of measurements to export
    """
    try:
        import pandas as pd
        from datetime import datetime
        
        validated_node = NodeID(value=node_id)
        measurement_list = [m.strip() for m in measurements.split(',')]
        
        data_service = SageDataService()
        user_token = get_current_user_token()
        
        all_data = []
        
        # Collect data for each measurement
        for measurement in measurement_list:
            data = data_service.query_data(
                start=time_range,
                filter_params={
                    "name": measurement,
                    "vsn": validated_node.value
                },
                user_token=user_token
            )
            
            if not data.empty:
                data['measurement'] = measurement
                all_data.append(data)
        
        if not all_data:
            return f"❌ No data found for node {node_id} with specified measurements"
        
        # Combine all data
        combined_data = pd.concat(all_data, ignore_index=True)
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sage_data_{node_id}_{timestamp}.csv"
        
        # Export to CSV (in production, you'd save to a file or return the data)
        csv_content = combined_data.to_csv(index=False)
        
        results = [
            f"📁 **Data Export Completed**",
            f"",
            f"**Node:** {node_id}",
            f"**Time Range:** {time_range}",
            f"**Measurements:** {', '.join(measurement_list)}",
            f"**Records:** {len(combined_data)}",
            f"**Suggested Filename:** {filename}",
            f"",
            f"**CSV Preview (first 10 lines):**",
            f"```csv"
        ]
        
        # Add preview of CSV content
        preview_lines = csv_content.split('\\n')[:10]
        results.extend(preview_lines)
        results.append("```")
        
        # In a real implementation, you might:
        # 1. Save to a temporary file and return the path
        # 2. Upload to cloud storage and return a download link
        # 3. Send via email
        # 4. Store in a database
        
        return "\\n".join(results)
        
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        return f"❌ Error exporting data: {str(e)}"
```

## Best Practices

### 1. Function Design

- **Clear documentation**: Write detailed docstrings with parameter descriptions
- **Input validation**: Use the existing validation classes (`NodeID`, `TimeRange`)
- **Error handling**: Wrap your code in try-catch blocks
- **Consistent return format**: Use formatted strings with emojis and markdown

### 2. Data Access

- **Use existing services**: Leverage `SageDataService` and other existing classes
- **Authentication**: Always use `get_current_user_token()` for protected data
- **Efficient queries**: Be mindful of data volume and query performance

### 3. Code Organization

```python
# Group related functions together
# ----------------------------------------
# CUSTOM ANALYSIS TOOLS
# ----------------------------------------

@mcp.tool()
def custom_function_1():
    """First custom function"""
    pass

@mcp.tool() 
def custom_function_2():
    """Second custom function"""
    pass
```

### 4. Testing

```python
# Add simple tests for your functions
def test_custom_function():
    """Test your custom function"""
    result = analyze_temperature_trends("W023", 1, 20.0)
    assert "Temperature Analysis" in result
    print("✅ Custom function test passed")

# Call tests in main() during development
def main():
    test_custom_function()  # Remove before production
    # ... rest of main function
```

## Deployment

### Local Development

```bash
# Test your changes
python sage_mcp.py

# Run with custom environment
export MCP_HOST=127.0.0.1
export MCP_PORT=8001
python sage_mcp.py
```

### Docker Deployment

```bash
# Build your custom image
docker build -t my-sage-mcp .

# Run with custom configuration
docker run -p 8000:8000 -e SAGE_USER_TOKEN="your_token" my-sage-mcp
```

### Production Considerations

1. **Environment Variables**: Use environment variables for configuration
2. **Logging**: Add appropriate logging for debugging
3. **Performance**: Consider caching for expensive operations
4. **Security**: Validate all inputs and handle authentication properly

## Troubleshooting

### Common Issues

**Function not appearing in MCP client:**
- Check for syntax errors in your function
- Ensure the `@mcp.tool()` decorator is present
- Restart the server after making changes

**Import errors:**
- Make sure all required packages are in `requirements.txt`
- Check that imports are at the top of the file

**Data access issues:**
- Verify authentication token is set correctly
- Check that node IDs and time ranges are valid
- Look at server logs for detailed error messages

**Performance problems:**
- Limit data queries to reasonable time ranges
- Consider pagination for large datasets
- Add progress indicators for long-running operations

### Debugging Tips

```python
# Add debug logging to your functions
import logging
logger = logging.getLogger(__name__)

@mcp.tool()
def debug_function(param: str) -> str:
    logger.info(f"Debug function called with param: {param}")
    try:
        # Your code here
        result = "success"
        logger.info(f"Debug function result: {result}")
        return result
    except Exception as e:
        logger.error(f"Debug function error: {e}")
        raise
```

### Getting Help

1. **Check the logs**: The server provides detailed logging
2. **Review existing functions**: Look at similar functions in `sage_mcp.py`
3. **Test incrementally**: Start with simple functions and add complexity
4. **Community**: Open issues on GitHub for help

## Contributing Back

If you create useful custom functions, consider contributing them back to the main repository:

1. **Fork and create a feature branch**
2. **Add comprehensive documentation**
3. **Include tests**
4. **Submit a pull request**

Your contributions help the entire SAGE community!

---

**Happy coding!** 🚀

For more information about SAGE and the MCP protocol, see:
- [SAGE Documentation](https://sagecontinuum.org)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol](https://modelcontextprotocol.io)
