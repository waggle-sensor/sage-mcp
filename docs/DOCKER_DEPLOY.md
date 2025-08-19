# Docker Deployment Guide

This guide covers multiple approaches to deploy the SAGE MCP Server using Docker with external access.

## Quick Start

The simplest way to run the server with external access:

```bash
# Build and run with Docker Compose (recommended)
docker-compose up --build

# Or build and run manually
docker build -t sage-mcp .
docker run -p 8000:8000 -e MCP_HOST=0.0.0.0 sage-mcp
```

The server will be accessible at `http://your-host-ip:8000`

## Deployment Options

### Option 1: Docker Compose (Recommended)

```bash
# External access (default)
docker-compose up sage-mcp

# Localhost only (secure)
docker-compose --profile local up sage-mcp-local
```

### Option 2: Direct Docker Run

```bash
# External access
docker run -d \
  --name sage-mcp \
  -p 8000:8000 \
  -e MCP_HOST=0.0.0.0 \
  -e MCP_PORT=8000 \
  --restart unless-stopped \
  sage-mcp

# Localhost only
docker run -d \
  --name sage-mcp-local \
  -p 127.0.0.1:8000:8000 \
  -e MCP_HOST=127.0.0.1 \
  -e MCP_PORT=8000 \
  --restart unless-stopped \
  sage-mcp
```

### Option 3: Custom Port

```bash
# Run on port 9000 instead of 8000
docker run -d \
  --name sage-mcp \
  -p 9000:9000 \
  -e MCP_HOST=0.0.0.0 \
  -e MCP_PORT=9000 \
  --restart unless-stopped \
  sage-mcp
```

## Server Implementation

The Docker container uses FastMCP's built-in HTTP server:

### FastMCP HTTP Server
- **File**: `sage_mcp.py`
- **Command**: `python sage_mcp.py`
- **Transport**: FastMCP's built-in "http" transport
- **Benefits**: 
  - Native FastMCP support
  - Full control over host/port binding
  - Production-ready with uvicorn internally
  - Simple configuration via environment variables

## Testing the Deployment

### Health Check
```bash
# Test basic connectivity
curl http://localhost:8000/

# Test from another machine (replace with your server IP)
curl http://YOUR_SERVER_IP:8000/
```

### MCP Protocol Test
```bash
# Basic MCP endpoint test
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
```

## Troubleshooting

### Server Not Accessible Externally
1. Check if `MCP_HOST=0.0.0.0` is set
2. Verify port mapping: `-p 8000:8000`
3. Check firewall settings on host
4. Ensure Docker daemon allows external connections

### Container Fails to Start
1. Check logs: `docker logs sage-mcp`
2. Verify environment variables are set correctly
3. Test the server directly:
   ```bash
   docker run -it --rm sage-mcp python sage_mcp.py
   ```

### Connection Timeouts
- Ensure no proxy is buffering the connection
- Check if the container has enough resources
- Verify the MCP client is compatible with the protocol version

## Security Considerations

### External Access (Production)
- Use a reverse proxy (nginx/Apache) with SSL
- Configure firewall rules
- Consider authentication middleware
- Monitor access logs

### Internal Access (Development)
- Use `127.0.0.1` binding for local-only access
- Run with docker-compose local profile
- Consider using Docker networks for service isolation

## Production Deployment

For production environments:

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  sage-mcp:
    image: sage-mcp:latest
    restart: always
    environment:
      - MCP_HOST=127.0.0.1  # Behind reverse proxy
      - MCP_PORT=8000
    networks:
      - internal
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.sage-mcp.rule=Host(`mcp.yourdomain.com`)"
      - "traefik.http.services.sage-mcp.loadbalancer.server.port=8000"

networks:
  internal:
    driver: bridge
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_HOST` | `0.0.0.0` | Host to bind to |
| `MCP_PORT` | `8000` | Port to listen on |
| `PYTHONUNBUFFERED` | `1` | Ensure logs appear in real-time |

## Build Arguments

```bash
# Custom Python version
docker build --build-arg PYTHON_VERSION=3.12 -t sage-mcp .

# Development build with extra tools
docker build --target development -t sage-mcp:dev .
```

## Troubleshooting

### Missing Dependencies Error

If you see errors like `No module named 'fastapi'` or `No module named 'starlette'`:

```bash
# Rebuild with no cache to ensure fresh dependencies
docker-compose build --no-cache

# Or rebuild the image manually
docker build --no-cache -t sage-mcp .
```

### Check Container Logs

```bash
# View logs for the running container
docker-compose logs sage-mcp

# Follow logs in real-time
docker-compose logs -f sage-mcp

# Check logs for a specific container ID
docker logs <container-id>
```

### Verify Dependencies

```bash
# Test if all dependencies are properly installed
docker run --rm sage-mcp python -c "
import fastmcp, fastapi, starlette, sage_data_client, httpx
print('✅ All dependencies imported successfully!')
"
```

### Common Issues

1. **Import Errors**: Rebuild with `--no-cache` to ensure fresh dependency installation
2. **Port Conflicts**: Make sure port 8000 is not in use by another service
3. **Memory Issues**: Ensure Docker has sufficient memory allocated (at least 2GB recommended)
4. **Network Issues**: Check firewall settings if external access is not working 