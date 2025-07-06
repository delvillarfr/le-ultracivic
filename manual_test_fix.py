#!/usr/bin/env python3
"""
Manual test to verify the reservation fix works
This simulates exactly what the frontend would do
"""

import requests
import json

# Configuration
BACKEND_URL = "http://localhost:8000/api"
TEST_WALLET = "0x742d35cc6634c0532925a3b8d11d2d7d2ae30b2b"

def test_reservation_manual():
    """Manually test the reservation endpoint"""
    
    print("=== Manual Reservation Test ===")
    print(f"Backend URL: {BACKEND_URL}")
    print()
    
    # Test data that frontend would send
    test_data = {
        "num_allowances": 1,
        "message": "Manual test reservation",
        "wallet": TEST_WALLET
    }
    
    print("Sending reservation request...")
    print(f"Data: {json.dumps(test_data, indent=2)}")
    print()
    
    try:
        # Make the request (this is what the frontend api.ts does)
        response = requests.post(
            f"{BACKEND_URL}/retirements",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if "order_id" in result:
                print(f"\n🎉 Reservation fix confirmed! Order ID: {result['order_id']}")
                return True
            else:
                print("\n❌ Response missing order_id field")
                return False
                
        else:
            print("❌ FAILED!")
            try:
                error_data = response.json()
                print(f"Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the backend server running?")
        print("Start it with: python -m uvicorn app.main:app --port 8000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_reservation_manual()
    
    if success:
        print("\n" + "="*50)
        print("✅ THE RESERVATION ISSUE HAS BEEN FIXED!")
        print("✅ Frontend can now successfully reserve allowances")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("❌ Issue still exists - check backend server")
        print("="*50)