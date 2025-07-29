#!/usr/bin/env python3

import requests
import json

def test_endpoint():
    """Test stored procedure endpoint without authentication"""
    
    # Test endpoint that bypasses authentication for testing
    url = "http://localhost:5000/api/debug/ujian-siswa/1/detail"
    
    try:
        # Create a session to maintain cookies if needed
        session = requests.Session()
        
        # Make request
        print(f"Testing endpoint: {url}")
        response = session.get(url)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Success! Response data:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"Raw response: {response.text}")
        else:
            print(f"❌ Error response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Make sure Flask server is running on port 5000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == '__main__':
    test_endpoint() 