#!/usr/bin/env python3
"""
Quick hackathon demo patch for Ultra Civic allowance reservation
This creates a minimal working demo by bypassing database issues
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional

# In-memory storage for demo
demo_allowances: Dict[str, Dict] = {}
demo_orders: Dict[str, Dict] = {}

# Initialize demo data
def init_demo_data():
    """Initialize some demo allowances"""
    global demo_allowances
    
    # Create 20 demo allowances
    for i in range(20):
        serial = f"UC-{2030000000 + i:06d}"
        demo_allowances[serial] = {
            "serial_number": serial,
            "status": "available",
            "order_id": None,
            "timestamp": None,
            "wallet": None,
            "message": None,
            "tx_hash": None,
            "reward_tx_hash": None
        }
    
    print(f"✅ Initialized {len(demo_allowances)} demo allowances")

def reserve_allowances(num_allowances: int, wallet: str, message: str) -> Dict:
    """Demo reservation logic"""
    global demo_allowances, demo_orders
    
    # Find available allowances
    available = [a for a in demo_allowances.values() if a["status"] == "available"]
    
    if len(available) < num_allowances:
        return {
            "success": False,
            "error": f"Only {len(available)} allowances available, need {num_allowances}"
        }
    
    # Reserve the allowances
    order_id = str(uuid.uuid4())
    reserved_serials = []
    
    for i in range(num_allowances):
        allowance = available[i]
        allowance["status"] = "reserved"
        allowance["order_id"] = order_id
        allowance["wallet"] = wallet
        allowance["message"] = message
        allowance["timestamp"] = datetime.now()
        reserved_serials.append(allowance["serial_number"])
    
    # Store order
    demo_orders[order_id] = {
        "order_id": order_id,
        "serial_numbers": reserved_serials,
        "status": "reserved",
        "wallet": wallet,
        "message": message,
        "timestamp": datetime.now()
    }
    
    return {
        "success": True,
        "order_id": order_id,
        "serial_numbers": reserved_serials
    }

def confirm_payment(order_id: str, tx_hash: str) -> Dict:
    """Demo payment confirmation"""
    global demo_orders, demo_allowances
    
    if order_id not in demo_orders:
        return {"success": False, "error": "Order not found"}
    
    order = demo_orders[order_id]
    
    # Update allowances to retired
    for serial in order["serial_numbers"]:
        if serial in demo_allowances:
            demo_allowances[serial]["status"] = "retired"
            demo_allowances[serial]["tx_hash"] = tx_hash
            demo_allowances[serial]["reward_tx_hash"] = f"0x{uuid.uuid4().hex}"
    
    order["status"] = "completed"
    order["tx_hash"] = tx_hash
    
    return {
        "success": True,
        "message": "Payment confirmed and allowances retired!",
        "order_id": order_id,
        "serial_numbers": order["serial_numbers"]
    }

def get_history() -> List[Dict]:
    """Get demo history"""
    global demo_orders
    
    completed_orders = [
        order for order in demo_orders.values() 
        if order["status"] == "completed"
    ]
    
    return sorted(completed_orders, key=lambda x: x["timestamp"], reverse=True)

def demo_flow():
    """Run a complete demo flow"""
    print("🚀 Ultra Civic Hackathon Demo Flow")
    print("=" * 50)
    
    # Initialize
    init_demo_data()
    
    # Step 1: Reserve allowances
    print("\n1. Reserving 3 allowances...")
    result = reserve_allowances(
        num_allowances=3,
        wallet="0x742d35Cc6634C0532925a3b8D6aC44dC5A25489e",
        message="Making the world greener! 🌱"
    )
    
    if result["success"]:
        print(f"✅ Reserved allowances: {result['serial_numbers']}")
        print(f"   Order ID: {result['order_id']}")
        order_id = result["order_id"]
    else:
        print(f"❌ Reservation failed: {result['error']}")
        return
    
    # Step 2: Confirm payment
    print("\n2. Confirming payment...")
    demo_tx_hash = f"0x{uuid.uuid4().hex}"
    payment_result = confirm_payment(order_id, demo_tx_hash)
    
    if payment_result["success"]:
        print(f"✅ Payment confirmed!")
        print(f"   Transaction: {demo_tx_hash}")
        print(f"   Retired allowances: {payment_result['serial_numbers']}")
    else:
        print(f"❌ Payment failed: {payment_result['error']}")
        return
    
    # Step 3: Show history
    print("\n3. Retirement history:")
    history = get_history()
    for entry in history:
        print(f"   Serial Numbers: {', '.join(entry['serial_numbers'])}")
        print(f"   Message: {entry['message']}")
        print(f"   Wallet: {entry['wallet']}")
        print(f"   Time: {entry['timestamp']}")
        print("")
    
    print("🎉 Demo complete! Ready for hackathon presentation.")

if __name__ == "__main__":
    demo_flow()