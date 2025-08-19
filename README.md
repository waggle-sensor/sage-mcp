# SAGE MCP Server

A Model Context Protocol (MCP) server for interacting with the SAGE (Software-Defined Sensor Network) platform. This server provides tools, resources, and prompts for querying sensor data, submitting jobs, and managing SAGE nodes.

## Features

- **Sensor Data Queries**: Access environmental, IIO, and other sensor data from SAGE nodes
- **Job Management**: Submit, monitor, and manage edge computing jobs
- **Plugin System**: Work with SAGE plugins and edge applications  
- **Documentation**: Built-in SAGE documentation and FAQ system
- **Authentication Support**: Support for protected data access with user tokens
- **Natural Language Queries**: Query data using natural language descriptions

## Authentication

The server supports **session-based authentication** for accessing protected SAGE data. Each user/client maintains isolated authentication credentials that don't interfere with other concurrent users. 

### Token Format
For protected data access, use the format: `username:access_token`
- Get your access token from: https://portal.sagecontinuum.org/account/access
- Format: `your_username:your_access_token`

### 1. MCP Tool (Recommended)
Use the built-in authentication tool to set your credentials:
```
Call the tool: set_authentication_token
Parameters:
  username: your_sage_username
  token: your_access_token_here
```

### 2. Environment Variable
Set your token as an environment variable before starting the server:
```bash
export SAGE_USER_TOKEN="username:your_access_token_here"
# or
export SAGE_ACCESS_TOKEN="username:your_access_token_here"
```

### 3. Programmatic Setting
Set the token programmatically in your code:
```python
from sage_mcp import set_user_token
set_user_token("username:your_access_token_here")
```

### Getting Your Access Token
1. Visit [SAGE Portal Access Credentials](https://portal.sagecontinuum.org/account/access)
2. Sign in with your SAGE account
3. Copy your access token from the credentials section
4. For protected data, ensure you have:
   - A valid SAGE account
   - Signed the Data Use Agreement
   - Appropriate permissions for the data you're accessing

### Token Format
Your token can be provided in two formats:
- Just the token: `your_token_here`
- Username and token: `username:your_token_here`

## Image Proxy

The server includes an image proxy endpoint that allows authenticated access to SAGE images:

### HTTP Endpoint
```
GET /proxy/image?url=<encoded_sage_url>&token=<optional_token>
```

### Authentication Methods (in priority order)
1. **Environment Variables** (recommended - like the SAGE Python examples):
   ```bash
   export SAGE_USER=your_username
   export SAGE_PASS=your_password
   ```

2. **Token parameter** in `username:password` format:
   ```bash
   curl "http://localhost:8000/proxy/image?url=...&token=username:password"
   ```

3. **Bearer token** for simple access tokens:
   ```bash
   curl "http://localhost:8000/proxy/image?url=...&token=your_access_token"
   ```

### MCP Tool
Use the `get_image_proxy_url()` tool to generate proxy URLs:
```python
# Get a proxy URL for a SAGE image
proxy_url = get_image_proxy_url("https://storage.sagecontinuum.org/api/v1/data/sage/...")
```

### Features
- **Multiple Auth Methods**: Environment variables, username:password tokens, or Bearer tokens
- **Security**: Only allows SAGE storage URLs
- **Caching**: Images are cached for 1 hour for better performance
- **Error Handling**: Proper HTTP status codes for authentication and access errors

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt

# Test that all dependencies are properly installed
python test_dependencies.py
```

## Usage

### Starting the Server

```bash
python sage_mcp.py
```

The server will start on `http://localhost:8000/mcp` by default.

### Environment Variables

- `MCP_HOST`: Host to bind to (default: `0.0.0.0`)
- `MCP_PORT`: Port to bind to (default: `8000`)

### Example Usage with Authentication

```bash
# Method 1: Using MCP tools (recommended)
# Start the server
python sage_mcp.py
# In your MCP client, call: set_authentication_token("username:your_access_token_here")
# Then use any data querying tool

# Method 2: Environment variable
export SAGE_USER_TOKEN="your_access_token_here"
python sage_mcp.py
# All tools will automatically use the token for protected data
```

## Available Tools

### Authentication Tools
- `set_authentication_token(username, token)` - Set your SAGE authentication credentials (per-session)
- `set_authentication_token_legacy(token)` - Set token in legacy format (deprecated)
- `get_authentication_status()` - Check if an authentication token is set for this session
- `list_active_sessions()` - List all active authenticated sessions (admin/debug tool)

### Sensor Data Tools
- `get_node_all_data(node_id, time_range)` - Get all sensor data for a node
- `get_node_iio_data(node_id, time_range)` - Get IIO sensor data
- `get_environmental_summary(node_id, time_range)` - Get environmental data summary
- `get_node_temperature(node_id, sensor_type)` - Get temperature data
- `get_temperature_summary(time_range, sensor_type)` - Get temperature summary
- `search_measurements(pattern, node_id, time_range)` - Search for measurements

### Node Information Tools  
- `list_available_nodes(time_range)` - List active SAGE nodes
- `get_node_info(node_id)` - Get detailed node information
- `list_all_nodes()` - List all SAGE nodes
- `get_sensor_details(sensor_type)` - Get sensor specifications

### Job Management Tools
- `submit_sage_job(job_name, nodes, plugin_image, ...)` - Submit custom jobs
- `submit_plugin_job(plugin_type, job_name, nodes)` - Submit pre-configured plugin jobs
- `check_job_status(job_id)` - Check job status
- `query_job_data(job_name, node_id, time_range)` - Query job output data

### Geographic Tools
- `get_nodes_by_location(location)` - Find nodes by geographic location
- `get_measurement_stat_by_location(location, measurement_type, stat, ...)` - Get statistics by location

### Plugin Tools
- `find_plugins_for_task(task_description)` - Find plugins for a task
- `get_plugin_data(plugin_id, nodes, time_range)` - Query plugin data
- `query_plugin_data_nl(query)` - Natural language plugin queries

### Image and Cloud Data Tools
- `get_cloud_images(time_range, node_id)` - Get cloud/sky images
- `get_image_data(time_range, node_id, plugin_pattern)` - Get image data
- `get_image_proxy_url(sage_url)` - Get a proxy URL for accessing SAGE images with authentication

### Documentation Tools
- `ask_sage_docs(question)` - Ask questions about SAGE documentation
- `sage_faq(topic)` - Get FAQ answers
- `search_sage_docs(query)` - Search documentation

## Resources

- `query://{plugin}` - Query data for specific plugins
- `stats://temperature` - Temperature statistics across nodes

## Prompts

- `getting_started_guide()` - Interactive guide for new users
- `plugin_development_guide()` - Guide for creating plugins
- `data_analysis_guide()` - Guide for data analysis
- `troubleshooting_guide()` - Troubleshooting help

## Docker Deployment

See [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md) for containerized deployment instructions.

## Development

The server is built using:
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [sage-data-client](https://github.com/sagecontinuum/sage-data-client) - SAGE data access
- [pandas](https://pandas.pydata.org/) - Data processing

## Extending with Custom Functions

Want to add your own custom MCP tools to the SAGE server? You can easily fork this repository and add custom endpoints:

```python
@mcp.tool()
def my_custom_analysis(data_query: str, analysis_type: str = "basic") -> str:
    """Perform custom analysis on SAGE data"""
    # Your custom logic here
    # Access SAGE data using the existing data_service
    # Return formatted results
    return "Analysis results..."
```

For detailed instructions on forking, adding custom functions, and deploying your enhanced server, see our [Custom Functions Guide](CUSTOM_FUNCTIONS.md).

## License

This project is licensed under the MIT License. 