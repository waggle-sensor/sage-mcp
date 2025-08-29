#!/usr/bin/env python3
"""
Test Sage authentication methods directly
"""

import os
import requests
import base64
from io import BytesIO
from PIL import Image

def test_sage_auth_direct():
    """Test Sage authentication directly using requests (like the working example)"""

    # Example Sage image URL
    url = "https://storage.sagecontinuum.org/api/v1/data/fire-detection-2420/sage-fire-detection-0.1.5/000048b02dd3c427/1754947969829525760-sample.jpg"

    print("Testing Sage authentication methods directly...")
    print(f"URL: {url}")
    print("-" * 80)

    # Method 1: Environment variables (like the working example)
    sage_user = os.getenv("SAGE_USER")
    sage_pass = os.getenv("SAGE_PASS")

    if sage_user and sage_pass:
        print("🔑 Testing with SAGE_USER and SAGE_PASS environment variables...")
        try:
            auth = (sage_user, sage_pass)
            response = requests.get(url, auth=auth, timeout=30)

            if response.status_code == 200:
                print("✅ Success with environment variables!")
                print(f"Content-Type: {response.headers.get('content-type')}")
                print(f"Content-Length: {len(response.content)} bytes")

                # Try to open as image
                try:
                    image = Image.open(BytesIO(response.content))
                    print(f"✅ Valid image: {image.size} pixels, mode: {image.mode}")
                except Exception as e:
                    print(f"❌ Invalid image data: {e}")

            else:
                print(f"❌ Failed with status {response.status_code}: {response.text}")

        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("⚠️  SAGE_USER and SAGE_PASS not found in environment")

    print()

    # Method 2: Test with Basic Auth header manually
    print("🔑 Testing with manual Basic Auth (if you provide credentials)...")

    # You can set these for testing
    test_username = input("Enter Sage username (or press Enter to skip): ").strip()
    if test_username:
        test_password = input("Enter Sage password: ").strip()

        try:
            credentials = base64.b64encode(f"{test_username}:{test_password}".encode()).decode()
            headers = {"Authorization": f"Basic {credentials}"}
            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                print("✅ Success with manual Basic Auth!")
                print(f"Content-Type: {response.headers.get('content-type')}")
                print(f"Content-Length: {len(response.content)} bytes")
            else:
                print(f"❌ Failed with status {response.status_code}: {response.text}")

        except Exception as e:
            print(f"❌ Error: {e}")

    print()

    # Method 3: Test without authentication (should fail for protected images)
    print("🔓 Testing without authentication (should fail for protected images)...")
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            print("✅ Public image - no auth required")
            print(f"Content-Length: {len(response.content)} bytes")
        elif response.status_code == 401:
            print("🔐 Authentication required (expected for protected images)")
        else:
            print(f"❌ Unexpected status: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_sage_auth_direct()