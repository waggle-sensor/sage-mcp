#!/usr/bin/env python3
"""
Test script to verify MCP authentication is working correctly.
Tests the specific authentication methods used by Cursor MCP client.
"""

import requests
import json
import base64
import sys

def test_mcp_auth_bearer():
    """Test MCP authentication with Bearer token"""
    print("🔍 Testing MCP Bearer token authentication...")
    
    try:
        headers = {
            "Authorization": "Bearer test-username:test-access-token",
            "Content-Type": "application/json"
        }
        
        # Test MCP tools endpoint
        url = "http://localhost:8000/mcp/tools"
        response = requests.post(url, headers=headers, json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        })
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if "result" in data and "tools" in data["result"]:
                print(f"✅ Bearer auth successful - found {len(data['result']['tools'])} tools")
                return True
        
        print(f"❌ Bearer auth failed: {response.text[:200]}")
        return False
        
    except Exception as e:
        print(f"❌ Error testing Bearer auth: {e}")
        return False

def test_mcp_auth_xsage():
    """Test MCP authentication with X-SAGE-Token header"""
    print("🔍 Testing MCP X-SAGE-Token authentication...")
    
    try:
        headers = {
            "X-SAGE-Token": "test-username:test-access-token",
            "Content-Type": "application/json"
        }
        
        # Test MCP tools endpoint
        url = "http://localhost:8000/mcp/tools"
        response = requests.post(url, headers=headers, json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        })
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if "result" in data and "tools" in data["result"]:
                print(f"✅ X-SAGE-Token auth successful - found {len(data['result']['tools'])} tools")
                return True
        
        print(f"❌ X-SAGE-Token auth failed: {response.text[:200]}")
        return False
        
    except Exception as e:
        print(f"❌ Error testing X-SAGE-Token auth: {e}")
        return False

def test_mcp_auth_basic():
    """Test MCP authentication with Basic auth"""
    print("🔍 Testing MCP Basic auth authentication...")
    
    try:
        # Encode credentials
        credentials = "test-username:test-access-token"
        encoded = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json"
        }
        
        # Test MCP tools endpoint
        url = "http://localhost:8000/mcp/tools"
        response = requests.post(url, headers=headers, json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        })
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if "result" in data and "tools" in data["result"]:
                print(f"✅ Basic auth successful - found {len(data['result']['tools'])} tools")
                return True
        
        print(f"❌ Basic auth failed: {response.text[:200]}")
        return False
        
    except Exception as e:
        print(f"❌ Error testing Basic auth: {e}")
        return False

def test_image_proxy_auth():
    """Test image proxy with authentication"""
    print("🔍 Testing image proxy authentication...")
    
    try:
        # Use the same image URL from your example
        image_url = "https://storage.sagecontinuum.org/api/v1/data/imagesampler-mobotix-2727/sage-imagesampler-mobotix-0.3.7/000048b02dd3c427/1755608410242881757-sample.jpg"
        
        headers = {
            "Authorization": "Bearer test-username:test-access-token"
        }
        
        params = {
            "url": image_url
        }
        
        # Test image proxy endpoint
        proxy_url = "http://localhost:8000/proxy/image"
        response = requests.get(proxy_url, headers=headers, params=params, timeout=30)
        
        print(f"Response status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'image' in content_type:
                print(f"✅ Image proxy auth successful - received {len(response.content)} bytes")
                return True
            else:
                print(f"❌ Image proxy returned non-image content: {content_type}")
                print(f"Response preview: {response.text[:200]}")
        else:
            print(f"❌ Image proxy failed: {response.text[:200]}")
        
        return False
        
    except Exception as e:
        print(f"❌ Error testing image proxy: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 SAGE MCP Authentication Test")
    print("=" * 50)
    
    # Test connectivity first
    try:
        response = requests.get("http://localhost:8000/mcp/tools", timeout=5)
        print(f"✅ Server is running (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Server not reachable: {e}")
        print("Make sure the server is running: python sage_mcp.py")
        sys.exit(1)
    
    print("\n🧪 Testing MCP Authentication Methods")
    print("=" * 50)
    
    # Test all authentication methods
    results = []
    
    results.append(("Bearer Token", test_mcp_auth_bearer()))
    results.append(("X-SAGE-Token", test_mcp_auth_xsage()))
    results.append(("Basic Auth", test_mcp_auth_basic()))
    results.append(("Image Proxy", test_image_proxy_auth()))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:15} {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed > 0:
        print("\n🎉 At least one authentication method is working!")
        print("\n💡 Recommended Cursor MCP configurations:")
        print("\n1. Bearer Token (Recommended):")
        print('   "Authorization": "Bearer test-username:test-access-token"')
        print("\n2. X-SAGE-Token:")
        print('   "X-SAGE-Token": "test-username:test-access-token"')
        print("\n3. Basic Auth:")
        print('   "Authorization": "Basic dGVzdC11c2VybmFtZTp0ZXN0LWFjY2Vzcy10b2tlbg=="')
    else:
        print("\n❌ All authentication tests failed.")
        print("Check server logs for debugging information.")
    
    return passed > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
