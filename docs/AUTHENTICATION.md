# Authentication Implementation for Sage MCP Server

This document describes the authentication feature implemented for the Sage MCP server to support protected data access.

## Overview

The Sage MCP server supports user authentication tokens to access protected data that requires:
- A valid Sage account
- Signed Data Use Agreement
- Appropriate permissions for the requested data

**Authentication is only supported through HTTP headers and query parameters.**

## Implementation Details

### 1. Middleware Architecture

The authentication is implemented using FastMCP middleware that:
- Extracts authentication tokens from HTTP headers and query parameters only
- Stores tokens in a context variable for the duration of the request
- Passes tokens to all data service calls
- Does NOT support environment variables, session storage, or programmatic token setting

```python
@mcp.middleware
async def auth_middleware(request, call_next):
    """Middleware to extract user token from request headers and query parameters"""
    # Extract token from Authorization header, X-SAGE-Token header, or query params
    # Set in context variable for request duration only
    # Process request
```

### 2. Token Extraction

Tokens can be provided in the following ways ONLY:

#### Authorization Header (Recommended)
```
# Basic Auth (username:token encoded in base64)
Authorization: Basic dXNlcm5hbWU6dG9rZW4=

# Bearer token
Authorization: Bearer username:token
```

#### Custom Header
```
X-SAGE-Token: username:token
```

#### Query Parameters
```
http://localhost:8000/mcp/tools?token=username:token
```

### 3. Data Service Integration

All data service methods accept an optional `user_token` parameter:

```python
def query_data(
    start: str,
    end: Optional[str] = None,
    filter_params: Optional[Dict[str, Any]] = None,
    user_token: Optional[str] = None
) -> pd.DataFrame:
```

### 4. sage_data_client Integration

The implementation tries multiple authentication approaches with sage_data_client:

1. **Direct token parameter**: `query_args["token"] = user_token`
2. **Auth parameter**: `query_args["auth"] = user_token`
3. **Username/password format**: Based on Sage documentation showing username and token as password

```python
# Method 3: Username/password format
if ':' in user_token:
    username, token = user_token.split(':', 1)
    query_args["username"] = username
    query_args["password"] = token
else:
    query_args["username"] = ""
    query_args["password"] = user_token
```

## Updated Components

### Core Files Modified

1. **`sage_mcp.py`**
   - Simplified authentication middleware to only extract from headers/query params
   - Added context variable for token storage (request-scoped only)
   - Updated all tool functions to pass user tokens
   - Removed session storage, environment variables, and programmatic token setting
   - Removed MCP authentication tools

2. **`sage_mcp_server/data_service.py`**
   - Added `user_token` parameter to all query methods
   - Added authentication logic for sage_data_client calls
   - Added helpful error messages for authentication failures

3. **`sage_mcp_server/plugin_query_service.py`**
   - Added `user_token` parameter to query methods
   - Updated natural language query processing

### All Tools Updated

Every tool that queries Sage data supports authentication through headers/query params:
- `get_node_all_data()`
- `get_node_iio_data()`
- `get_environmental_summary()`
- `get_node_temperature()`
- `get_temperature_summary()`
- `search_measurements()`
- `query_job_data()`
- `get_measurement_stat_by_location()`
- `get_cloud_images()`
- `get_image_data()`
- `query_plugin_data_nl()`
- `get_plugin_data()`

## Usage Examples

### Authorization Header Authentication (Recommended)
```bash
# Start the server
python sage_mcp.py

# Query protected data using Authorization header with Basic Auth
echo -n "username:token" | base64
curl -H "Authorization: Basic dXNlcm5hbWU6dG9rZW4=" \
     "http://localhost:8000/mcp/resources/stats%3A%2F%2Ftemperature"

# Query protected data using Bearer token
curl -H "Authorization: Bearer username:token" \
     "http://localhost:8000/mcp/resources/stats%3A%2F%2Ftemperature"
```

### Custom Header Authentication
```bash
# Start the server
python sage_mcp.py

# Query protected data using custom header
curl -H "X-SAGE-Token: username:token" \
     "http://localhost:8000/mcp/resources/stats%3A%2F%2Ftemperature"
```

### Query Parameter Authentication
```bash
# Start the server
python sage_mcp.py

# Query protected data using query parameter
curl "http://localhost:8000/mcp/resources/stats%3A%2F%2Ftemperature?token=username:token"
```

### HTTP Header Authentication (Recommended)
```bash
# Basic Auth with base64 encoding
echo -n "username:token" | base64
curl -H "Authorization: Basic dXNlcm5hbWU6dG9rZW4=" \
     "http://localhost:8000/mcp/resources/stats%3A%2F%2Ftemperature"

# Bearer token
curl -H "Authorization: Bearer username:token" \
     "http://localhost:8000/mcp/resources/stats%3A%2F%2Ftemperature"

# Custom header
curl -H "X-SAGE-Token: username:token" \
     "http://localhost:8000/mcp/resources/stats%3A%2F%2Ftemperature"
```

## Error Handling

The implementation provides helpful error messages for authentication failures:

```
Authentication failed. Please check your token and permissions.
For protected data access, you need:
1. A valid Sage account
2. Signed Data Use Agreement
3. Valid access token from https://portal.sagecontinuum.org/account/access
4. Token format: 'username:token'
```

## Token Formats Supported

For protected data access, use the format: **Username:token**: `username:your_access_token_here`

- Simple tokens without username will only work for public data access
- Get your access token from: https://portal.sagecontinuum.org/account/access

## Security Considerations

- Tokens are stored in memory only for the duration of each request
- No tokens are logged or persisted
- No session storage or environment variable fallbacks
- Middleware gracefully handles token extraction failures
- All data queries continue to work without authentication for public data
- Authentication is stateless - each request must include credentials

## Future Enhancements

Potential improvements could include:
- Token validation and caching
- Support for OAuth2 flows
- Role-based access control
- Token refresh mechanisms

## Testing

Authentication can be tested using standard HTTP tools:

```bash
# Test with curl
curl -H "Authorization: Bearer username:token" \
     "http://localhost:8000/mcp/resources/stats%3A%2F%2Ftemperature"

# Test with query parameter
curl "http://localhost:8000/mcp/resources/stats%3A%2F%2Ftemperature?token=username:token"
```

## Removed Features

The following authentication methods have been **removed** and are no longer supported:

- Environment variable authentication (`SAGE_USER_TOKEN`, `SAGE_ACCESS_TOKEN`)
- Session-based token storage
- Thread-local token storage
- MCP authentication tools (`set_authentication_token`, `get_authentication_status`, etc.)
- Programmatic token setting (`set_user_token`)
- Context-based token extraction (non-HTTP)

**Only HTTP headers and query parameters are supported for authentication.**