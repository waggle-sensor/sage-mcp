#!/usr/bin/env python3
"""
Test script for the Sage Image Proxy endpoint
"""

import asyncio
import httpx
import urllib.parse

async def test_image_proxy():
    """Test the image proxy endpoint"""

    # Example Sage image URL (this is a real URL from the documentation)
    sage_url = "https://storage.sagecontinuum.org/api/v1/data/sage/sage-imagesampler-left-0.2.3/000048b02d05a0a4/1631279967237651354-2021-09-10T13:19:26+0000.jpg"

    # Encode the URL for use as a query parameter
    encoded_url = urllib.parse.quote(sage_url, safe='')

    # Test URL (assuming server is running on localhost:8000)
    proxy_url = f"http://localhost:8000/proxy/image?url={encoded_url}"

    print(f"Testing image proxy with URL: {sage_url}")
    print(f"Proxy URL: {proxy_url}")
    print("-" * 80)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Test without authentication first
            print("Testing without authentication...")
            response = await client.get(proxy_url)

            if response.status_code == 200:
                print("✅ Success! Image retrieved successfully")
                print(f"Content-Type: {response.headers.get('content-type')}")
                print(f"Content-Length: {len(response.content)} bytes")
                print(f"Cache-Control: {response.headers.get('cache-control')}")
                print(f"X-Sage-Proxy: {response.headers.get('x-sage-proxy')}")
            elif response.status_code == 401:
                print("🔐 Authentication required (expected for protected images)")
                print(f"Response: {response.text}")
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                print(f"Response: {response.text}")

        except httpx.ConnectError:
            print("❌ Connection failed - make sure the server is running on localhost:8000")
        except httpx.TimeoutException:
            print("❌ Request timed out")
        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n" + "=" * 80)
    print("Authentication options:")
    print("1. Environment variables (recommended):")
    print("   export SAGE_USER=your_username")
    print("   export SAGE_PASS=your_password")
    print()
    print("2. Token parameter with username:password:")
    print(f'   curl "{proxy_url}&token=username:password"')
    print()
    print("3. Token parameter with simple token:")
    print(f'   curl "{proxy_url}&token=your_access_token"')
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_image_proxy())