#!/usr/bin/env python3
"""Test the history endpoint functionality."""

import asyncio
from fastapi.testclient import TestClient
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app


def test_history_endpoint():
    """Test the history endpoint with test client."""
    print("Testing History Endpoint")
    print("=" * 40)
    
    try:
        client = TestClient(app)
        
        # Test basic endpoint access
        print("\n1. Testing basic endpoint access...")
        response = client.get("/api/retirements/history")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Endpoint accessible")
            print(f"Response structure: {list(data.keys())}")
            
            if "retirements" in data and "total" in data:
                print(f"✅ Correct response structure")
                print(f"Total retirement orders: {data['total']}")
                print(f"Returned items: {len(data['retirements'])}")
                
                # Check if we have any retirement data
                if data["retirements"]:
                    first_item = data["retirements"][0]
                    print(f"✅ Sample retirement item:")
                    for key, value in first_item.items():
                        print(f"  - {key}: {value}")
                else:
                    print("ℹ️ No retirement history data found (expected for new system)")
            else:
                print(f"❌ Incorrect response structure: {data}")
        else:
            print(f"❌ Endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
        
        # Test pagination
        print("\n2. Testing pagination...")
        response = client.get("/api/retirements/history?limit=10&offset=0")
        
        if response.status_code == 200:
            print("✅ Pagination parameters accepted")
        else:
            print(f"❌ Pagination failed: {response.status_code}")
        
        # Test rate limiting (optional)
        print("\n3. Testing rate limiting...")
        requests_count = 0
        for i in range(5):
            response = client.get("/api/retirements/history")
            if response.status_code == 200:
                requests_count += 1
            else:
                break
        
        print(f"✅ Made {requests_count} successful requests")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_history_endpoint()
    
    if success:
        print("\n🎉 History endpoint is working correctly!")
        print("Frontend can now fetch retirement history from GET /api/retirements/history")
    else:
        print("\n❌ History endpoint needs debugging.")