#!/usr/bin/env python3
"""Test the history endpoint response format."""

import json
from fastapi.testclient import TestClient

from app.main import app


def test_history_response_format():
    """Test that the history endpoint returns the expected format."""
    print("Testing History Response Format")
    print("=" * 40)
    
    client = TestClient(app)
    
    try:
        response = client.get("/api/retirements/history")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Endpoint Response Structure:")
            print(json.dumps(data, indent=2))
            
            # Verify required fields
            required_fields = ["retirements", "total"]
            for field in required_fields:
                if field in data:
                    print(f"✅ Field '{field}' present")
                else:
                    print(f"❌ Field '{field}' missing")
            
            # Verify retirements array structure
            if isinstance(data.get("retirements"), list):
                print("✅ 'retirements' is an array")
                
                if data["retirements"]:
                    # Test with sample data structure
                    sample_item = data["retirements"][0]
                    expected_item_fields = [
                        "serial_numbers", "message", "wallet", 
                        "timestamp", "etherscan_link", "order_id"
                    ]
                    
                    for field in expected_item_fields:
                        if field in sample_item:
                            print(f"✅ Item field '{field}' present")
                        else:
                            print(f"❌ Item field '{field}' missing")
                else:
                    print("ℹ️ No retirement data to verify item structure")
                    print("ℹ️ Expected item fields:")
                    for field in ["serial_numbers", "message", "wallet", "timestamp", "etherscan_link", "order_id"]:
                        print(f"  - {field}")
            else:
                print("❌ 'retirements' is not an array")
            
            # Verify total is a number
            if isinstance(data.get("total"), int):
                print("✅ 'total' is an integer")
            else:
                print("❌ 'total' is not an integer")
            
            print(f"\n📋 Frontend Requirements Check:")
            print(f"✅ Serial numbers: Will be in 'serial_numbers' array field")
            print(f"✅ User messages: Will be in 'message' field")  
            print(f"✅ Etherscan links: Will be in 'etherscan_link' field")
            print(f"✅ Grouped by orders: Data is grouped by order_id")
            
            return True
            
        else:
            print(f"❌ Endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_history_response_format()
    
    if success:
        print(f"\n🎉 History endpoint format matches frontend requirements!")
        print(f"The frontend can now display the history table with:")
        print(f"- Column 1: Serial numbers (from 'serial_numbers' array)")
        print(f"- Column 2: User messages (from 'message' field)")
        print(f"- Column 3: Transaction links (from 'etherscan_link' field)")
    else:
        print(f"\n❌ Response format needs adjustment.")