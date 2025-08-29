#!/usr/bin/env python3
"""
Test script to verify authentication functionality in the Sage MCP server.
Tests only HTTP header and query parameter authentication methods.
"""

import requests
import json
import sys
import base64
from urllib.parse import urlencode

def test_without_auth():
    """Test request without authentication token"""
    print("🔍 Testing request without authentication...")

    try:
        url = "http://localhost:8000/mcp/tools"
        response = requests.get(url)

        if response.status_code == 200:
            print("✅ Request without auth successful")
            return True
        else:
            print(f"❌ Request failed with status {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_authorization_header_basic(token):
    """Test authentication using Authorization header with Basic auth"""
    print("🔍 Testing Authorization header with Basic auth...")

    try:
        # Encode token in base64 for Basic auth
        encoded_token = base64.b64encode(token.encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded_token}"
        }

        url = "http://localhost:8000/mcp/resources/stats%3A%2F%2Ftemperature"
        response = requests.get(url, headers=headers)

        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Authorization header Basic auth successful")
            return True
        else:
            print(f"❌ Authorization header Basic auth failed: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Error testing Authorization header Basic auth: {e}")
        return False

def test_authorization_header_bearer(token):
    """Test authentication using Authorization header with Bearer token"""
    print("🔍 Testing Authorization header with Bearer token...")

    try:
        headers = {
            "Authorization": f"Bearer {token}"
        }

        url = "http://localhost:8000/mcp/resources/stats%3A%2F%2Ftemperature"
        response = requests.get(url, headers=headers)

        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Authorization header Bearer auth successful")
            return True
        else:
            print(f"❌ Authorization header Bearer auth failed: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Error testing Authorization header Bearer auth: {e}")
        return False

def test_custom_header(token):
    """Test authentication using X-SAGE-Token custom header"""
    print("🔍 Testing X-SAGE-Token custom header...")

    try:
        headers = {
            "X-SAGE-Token": token
        }

        url = "http://localhost:8000/mcp/resources/stats%3A%2F%2Ftemperature"
        response = requests.get(url, headers=headers)

        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            print("✅ X-SAGE-Token custom header successful")
            return True
        else:
            print(f"❌ X-SAGE-Token custom header failed: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Error testing X-SAGE-Token custom header: {e}")
        return False

def test_query_parameter(token):
    """Test authentication using query parameter"""
    print("🔍 Testing query parameter authentication...")

    try:
        params = {"token": token}
        url = "http://localhost:8000/mcp/resources/stats%3A%2F%2Ftemperature"
        response = requests.get(url, params=params)

        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Query parameter auth successful")
            return True
        else:
            print(f"❌ Query parameter auth failed: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Error testing query parameter auth: {e}")
        return False

def test_temperature_query_with_auth(token):
    """Test a temperature query with authentication"""
    print("🔍 Testing temperature query with authentication...")

    try:
        headers = {
            "Authorization": f"Bearer {token}"
        }

        url = "http://localhost:8000/mcp/resources/stats%3A%2F%2Ftemperature"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            print("✅ Temperature query with auth successful")
            print(f"Response length: {len(response.text)} characters")
            # Show first few lines of response
            lines = response.text.split('\n')[:5]
            for line in lines:
                print(f"   {line}")
            return True
        else:
            print(f"❌ Temperature query failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Error testing temperature query: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Sage MCP Server Authentication Test")
    print("=" * 50)

    # Test basic connectivity first
    if not test_without_auth():
        print("\n❌ Basic connectivity test failed. Server may not be running.")
        sys.exit(1)

    # Get token from user
    token = input("\n🔑 Enter your Sage token (username:access_token format): ").strip()

    if not token:
        print("❌ No token provided. Testing only unauthenticated requests.")
        sys.exit(0)

    if ':' not in token:
        print("⚠️ Warning: Token should be in 'username:access_token' format for protected data access.")

    print(f"\n🧪 Testing authentication with token: {token[:10]}...{token[-4:] if len(token) > 14 else ''}")
    print("=" * 50)

    # Test all authentication methods
    results = []

    # Test Authorization header with Basic auth
    results.append(("Authorization Basic", test_authorization_header_basic(token)))

    # Test Authorization header with Bearer token
    results.append(("Authorization Bearer", test_authorization_header_bearer(token)))

    # Test custom header
    results.append(("X-SAGE-Token Header", test_custom_header(token)))

    # Test query parameter
    results.append(("Query Parameter", test_query_parameter(token)))

    # Test actual data query
    results.append(("Temperature Query", test_temperature_query_with_auth(token)))

    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1

    print(f"\nPassed: {passed}/{len(results)} tests")

    if passed == len(results):
        print("🎉 All authentication tests passed!")
        sys.exit(0)
    else:
        print("⚠️ Some authentication tests failed.")
        print("\nTroubleshooting:")
        print("- Make sure the server is running: python sage_mcp.py")
        print("- Check your token format: username:access_token")
        print("- Verify your Sage account has the required permissions")
        print("- Get your token from: https://portal.sagecontinuum.org/account/access")
        sys.exit(1)

if __name__ == "__main__":
    main()