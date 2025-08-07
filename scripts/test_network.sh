#!/bin/bash

echo "🔍 Testing SAGE MCP Server Network Access"
echo "========================================"

# Get container info
echo "📋 Docker Container Status:"
docker ps | grep sage

echo -e "\n🌐 Port Mapping Check:"
docker port $(docker ps -q --filter name=sage) 2>/dev/null || echo "No container running"

# Test different endpoints
echo -e "\n🧪 Testing Endpoints:"

endpoints=(
    "http://localhost:8000/"
    "http://localhost:8000/mcp"
    "http://localhost:8000/mcp/"
    "http://127.0.0.1:8000/"
    "http://127.0.0.1:8000/mcp"
    "http://127.0.0.1:8000/mcp/"
)

for endpoint in "${endpoints[@]}"; do
    echo -n "Testing $endpoint ... "
    response=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint" 2>/dev/null)
    if [ "$response" = "200" ]; then
        echo "✅ OK ($response)"
    elif [ "$response" = "307" ]; then
        echo "🔄 Redirect ($response)"
    elif [ "$response" = "000" ]; then
        echo "❌ No connection"
    else
        echo "⚠️  Status: $response"
    fi
done

# Test from inside container if possible
echo -e "\n🐳 Testing from inside container:"
container_id=$(docker ps -q --filter name=sage)
if [ ! -z "$container_id" ]; then
    echo "Container ID: $container_id"
    docker exec "$container_id" curl -s -o /dev/null -w "Internal /mcp/: %{http_code}\n" http://localhost:8000/mcp/ 2>/dev/null || echo "Failed to test inside container"
else
    echo "No running container found"
fi

# Check system networking
echo -e "\n🔧 System Network Check:"
echo "Listening on port 8000:"
netstat -tuln | grep :8000 || lsof -i :8000 || echo "Port 8000 not found in netstat/lsof"

# Test external IP if available
echo -e "\n🌍 External IP Test:"
external_ip=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "unknown")
if [ "$external_ip" != "unknown" ]; then
    echo "Your external IP: $external_ip"
    echo "Try: curl http://$external_ip:8000/mcp/"
else
    echo "Could not determine external IP"
fi

echo -e "\n💡 Quick Fixes to Try:"
echo "1. curl http://localhost:8000/mcp/ (with trailing slash)"
echo "2. Check firewall: sudo ufw status"
echo "3. Check Docker logs: docker logs sage-mcp"
echo "4. Rebuild: docker-compose down && docker-compose up --build" 