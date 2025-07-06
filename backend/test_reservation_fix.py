#!/usr/bin/env python3

import asyncio
import json
import subprocess
import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_reservation_endpoint():
    """Test the reservation endpoint"""
    test_data = {
        "num_allowances": 1,
        "message": "Test reservation",
        "wallet": "0x742d35cc6634c0532925a3b8d11d2d7d2ae30b2b"
    }
    
    print("Testing POST /api/retirements...")
    response = client.post("/api/retirements", json=test_data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ Reservation endpoint is working!")
        return response.json()
    else:
        print("❌ Reservation endpoint failed!")
        return None

def test_health_endpoint():
    """Test the health endpoint"""
    print("Testing GET /health...")
    response = client.get("/health")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ Health endpoint is working!")
    else:
        print("❌ Health endpoint failed!")

if __name__ == "__main__":
    print("=== Testing Backend API ===")
    test_health_endpoint()
    print()
    order = test_reservation_endpoint()
    
    if order and "order_id" in order:
        print(f"\n✅ Successfully created order: {order['order_id']}")
        print("🎉 The reservation issue has been fixed!")
    else:
        print("\n❌ Reservation still failing")