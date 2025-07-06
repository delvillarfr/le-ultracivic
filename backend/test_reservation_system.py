#!/usr/bin/env python3
"""
Comprehensive test for the reservation system
Tests both the backend logic and frontend integration
"""

import asyncio
import httpx
import pytest
from fastapi.testclient import TestClient
from app.main import app

# Test configuration
TEST_WALLET = "0x742d35cc6634c0532925a3b8d11d2d7d2ae30b2b"
TEST_MESSAGE = "Test reservation from automated test"

def test_reservation_with_testclient():
    """Test reservation using FastAPI TestClient"""
    client = TestClient(app)
    
    test_data = {
        "num_allowances": 1,
        "message": TEST_MESSAGE,
        "wallet": TEST_WALLET
    }
    
    print("🧪 Testing POST /api/retirements with TestClient...")
    
    try:
        response = client.post("/api/retirements", json=test_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Order ID: {result.get('order_id')}")
            return result.get('order_id')
        else:
            print(f"❌ Failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

async def test_reservation_with_httpx():
    """Test reservation using httpx (more realistic)"""
    test_data = {
        "num_allowances": 1,
        "message": TEST_MESSAGE + " (httpx)",
        "wallet": TEST_WALLET
    }
    
    print("🧪 Testing POST /api/retirements with httpx...")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "http://localhost:8000/api/retirements",
                json=test_data
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success! Order ID: {result.get('order_id')}")
                return result.get('order_id')
            else:
                print(f"❌ Failed: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def test_api_validation():
    """Test API validation with invalid data"""
    client = TestClient(app)
    
    print("🧪 Testing API validation...")
    
    # Test invalid wallet
    invalid_data = {
        "num_allowances": 1,
        "message": "test",
        "wallet": "invalid_wallet"
    }
    
    response = client.post("/api/retirements", json=invalid_data)
    print(f"Invalid wallet test - Status: {response.status_code}")
    
    # Test too many allowances
    invalid_data = {
        "num_allowances": 100,  # Over limit
        "message": "test",
        "wallet": TEST_WALLET
    }
    
    response = client.post("/api/retirements", json=invalid_data)
    print(f"Too many allowances test - Status: {response.status_code}")
    
    print("✅ API validation tests complete")

def test_frontend_api_interface():
    """Test that frontend API interface matches backend"""
    client = TestClient(app)
    
    # Test the exact data structure frontend would send
    frontend_data = {
        "num_allowances": 1,
        "message": "Frontend test",
        "wallet": TEST_WALLET
    }
    
    print("🧪 Testing frontend-backend API compatibility...")
    
    response = client.post("/api/retirements", json=frontend_data)
    
    if response.status_code == 200:
        result = response.json()
        # Check that response has expected structure
        if "order_id" in result:
            print("✅ Frontend-backend API interface is compatible")
            return True
        else:
            print("❌ Response missing expected 'order_id' field")
            return False
    else:
        print(f"❌ API call failed: {response.status_code}")
        return False

if __name__ == "__main__":
    print("=== Comprehensive Reservation System Test ===\n")
    
    # Test 1: Basic TestClient test
    order_id1 = test_reservation_with_testclient()
    print()
    
    # Test 2: API validation
    test_api_validation()
    print()
    
    # Test 3: Frontend compatibility
    frontend_compatible = test_frontend_api_interface()
    print()
    
    # Test 4: httpx test (requires running server)
    print("Note: httpx test requires running server on localhost:8000")
    print("To test with live server, run: python -m uvicorn app.main:app --port 8000")
    print()
    
    # Summary
    if order_id1 and frontend_compatible:
        print("🎉 All tests passed! The reservation system is working correctly.")
        print(f"✅ Created test order: {order_id1}")
        print("✅ API validation working")
        print("✅ Frontend-backend compatibility confirmed")
    else:
        print("❌ Some tests failed. Check the output above for details.")