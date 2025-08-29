# SAGE MCP Examples

This document provides practical examples of how to interact with the SAGE MCP server using natural language prompts. These examples work with AI assistants like Claude, ChatGPT, or through AI-powered IDEs like Cursor.

## Temperature and Environmental Data

### Basic Queries

```
"Show me current temperature readings from node W023"

"Get temperature data from all nodes in the last hour"

"Find the node with the highest temperature in the last day"

"Show me atmospheric pressure readings from all nodes in the last 2 hours"

"Get environmental summary including temperature, humidity, and pressure for node W06D"
```

### Advanced Analysis

```
"Compare temperature readings between urban and rural nodes"

"Show me temperature anomalies from the past week - anything above 35°C or below -10°C"

"Get both environment temperature (bme680) and internal temperature (bme280) for node W019"

"Find the location with the highest barometric pressure right now"

"Show me humidity patterns across different ecosystems"
```

## Node Information and Discovery

```
"List all available SAGE nodes and their current status"

"Find nodes in Chicago area"

"Get detailed information about node W023 including its sensors and location"

"Find all nodes in the Midwest region"

"What compute resources are available on node W06D?"
```

## Image and Camera Data

```
"Show me recent camera images from node W019"

"Get cloud cover images from the last 2 hours"

"Get images from the top camera on node W020"

"Show me recent flowering plant detection results"

"Find any motion detection results from the past hour"
```

## Plugin Discovery and Management

### Finding and Using Plugins

```
"Find plugins for monitoring bird sounds"

"What computer vision plugins are available for plant detection?"

"Show me data from the cloud cover detection plugin"

"Find plugins for air quality monitoring"

"Get recent results from audio sampling plugins"
```

### Plugin Development

```
"Help me create a plugin for detecting invasive plant species"

"Generate a bird species detection plugin that analyzes audio recordings"

"Create a plugin for monitoring air quality using environmental sensors"
```

## Job Submission and Management

```
"Deploy a cloud cover detection job to nodes W019 and W020"

"Check the status of job 12345"

"Show me recent data from my flowering plant detection job"

"Deploy air quality monitoring to urban nodes"

"Show me all active jobs currently running across the SAGE network"
```

## Advanced Analysis Examples

### Statistical Queries

```
"What's the maximum temperature recorded in Chicago nodes over the last day?"

"Calculate average atmospheric pressure across all Midwest nodes"

"Compare air quality between urban and rural SAGE nodes"

"Show me rainfall data from all nodes in the last 48 hours"
```

### Research Applications

```
"Help me test if urban heat islands affect local flowering patterns"

"Compare biodiversity metrics between prairie, forest, and wetland nodes"

"Show me temperature trends at node W06D over the past year"

"Find correlations between flowering plants and bird activity"
```

## Data Discovery and System Health

```
"What types of environmental measurements are available?"

"Show me details about BME680 environmental sensors"

"Which nodes haven't reported data in the last hour?"

"Check for any unusual sensor readings that might indicate hardware issues"
```

## Tips for Effective Queries

- Include time ranges (e.g., "last 24 hours", "past week")
- Specify node IDs when you know them (e.g., "node W023")
- Ask questions as you would to a colleague
- Start with broad queries, then narrow down based on results
- Combine multiple concepts in one query for comprehensive analysis

## Related Documentation

- [Getting Started Guide](GETTING_STARTED.md): Complete setup and usage instructions
- [Authentication Guide](AUTHENTICATION.md): How to set up credentials and access
- [Custom Functions](CUSTOM_FUNCTIONS.md): Advanced customization options

## Support

- **Documentation**: [SAGE Docs](https://docs.sagecontinuum.org)
- **Portal**: [SAGE Portal](https://portal.sagecontinuum.org)
- **Community**: [SAGE Forums](https://github.com/waggle-sensor/waggle/discussions)
- **Support**: sage-support@anl.gov
