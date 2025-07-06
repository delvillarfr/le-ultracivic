#!/usr/bin/env python3
"""
FastAPI demo endpoints for hackathon - bypasses database issues
Add these endpoints to your router for quick demo
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import uuid
from datetime import datetime

# Demo router
demo_router = APIRouter(prefix="/demo", tags=["demo"])

# In-memory storage for demo
demo_data = {
    "allowances": {},
    "orders": {}
}

class DemoRetirementRequest(BaseModel):
    num_allowances: int
    wallet: str
    message: str = ""

class DemoConfirmRequest(BaseModel):
    order_id: str
    tx_hash: str

# Initialize demo data
def init_demo_allowances():
    """Initialize demo allowances if not already done"""
    if not demo_data["allowances"]:
        for i in range(50):
            serial = f"UC-{2030000000 + i:06d}"
            demo_data["allowances"][serial] = {
                "serial_number": serial,
                "status": "available",
                "order_id": None,
                "timestamp": None,
                "wallet": None,
                "message": None,
                "tx_hash": None,
                "reward_tx_hash": None
            }

@demo_router.post("/retirements")
async def demo_create_retirement(request: DemoRetirementRequest):
    """Demo retirement endpoint - bypasses database"""
    init_demo_allowances()
    
    # Validate input
    if request.num_allowances < 1 or request.num_allowances > 99:
        raise HTTPException(status_code=400, detail="Number of allowances must be between 1 and 99")
    
    # Find available allowances
    available = [a for a in demo_data["allowances"].values() if a["status"] == "available"]
    
    if len(available) < request.num_allowances:
        raise HTTPException(
            status_code=400, 
            detail=f"Only {len(available)} allowances available, need {request.num_allowances}"
        )
    
    # Reserve allowances
    order_id = str(uuid.uuid4())
    reserved_serials = []
    
    for i in range(request.num_allowances):
        allowance = available[i]
        allowance["status"] = "reserved"
        allowance["order_id"] = order_id
        allowance["wallet"] = request.wallet
        allowance["message"] = request.message
        allowance["timestamp"] = datetime.now()
        reserved_serials.append(allowance["serial_number"])
    
    # Store order
    demo_data["orders"][order_id] = {
        "order_id": order_id,
        "serial_numbers": reserved_serials,
        "status": "reserved",
        "wallet": request.wallet,
        "message": request.message,
        "timestamp": datetime.now()
    }
    
    return {"order_id": order_id}

@demo_router.post("/retirements/confirm")
async def demo_confirm_payment(request: DemoConfirmRequest):
    """Demo payment confirmation - bypasses blockchain validation"""
    if request.order_id not in demo_data["orders"]:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = demo_data["orders"][request.order_id]
    
    # Update allowances to retired
    for serial in order["serial_numbers"]:
        if serial in demo_data["allowances"]:
            demo_data["allowances"][serial]["status"] = "retired"
            demo_data["allowances"][serial]["tx_hash"] = request.tx_hash
            demo_data["allowances"][serial]["reward_tx_hash"] = f"0x{uuid.uuid4().hex}"
    
    order["status"] = "completed"
    order["tx_hash"] = request.tx_hash
    
    return {
        "message": "Payment confirmed and allowances retired!",
        "status": "processing",
        "order_id": request.order_id,
        "next_steps": "Your allowances have been retired successfully!"
    }

@demo_router.get("/retirements/status/{order_id}")
async def demo_get_order_status(order_id: str):
    """Demo order status - returns completed immediately"""
    if order_id not in demo_data["orders"]:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = demo_data["orders"][order_id]
    
    return {
        "order_id": order_id,
        "status": "completed" if order["status"] == "completed" else "pending",
        "serial_numbers": order["serial_numbers"] if order["status"] == "completed" else None,
        "message": order["message"],
        "tx_hash": order.get("tx_hash"),
        "reward_tx_hash": f"0x{uuid.uuid4().hex}" if order["status"] == "completed" else None
    }

@demo_router.get("/retirements/history")
async def demo_get_history():
    """Demo history endpoint"""
    completed_orders = [
        {
            "serial_numbers": order["serial_numbers"],
            "message": order["message"],
            "wallet": order["wallet"],
            "timestamp": order["timestamp"].isoformat(),
            "etherscan_link": f"https://sepolia.etherscan.io/tx/{order.get('tx_hash', '0x' + uuid.uuid4().hex)}",
            "order_id": order["order_id"]
        }
        for order in demo_data["orders"].values()
        if order["status"] == "completed"
    ]
    
    return {
        "retirements": sorted(completed_orders, key=lambda x: x["timestamp"], reverse=True),
        "total": len(completed_orders)
    }

# Instructions for using this patch:
"""
To use this demo patch:

1. Add to your main.py:
   ```python
   from demo_api_patch import demo_router
   app.include_router(demo_router)
   ```

2. Update your frontend to use /demo/retirements instead of /retirements

3. The demo endpoints work exactly like the real ones but bypass:
   - Database connections
   - Blockchain validation
   - External API calls

4. Perfect for hackathon demos!
"""