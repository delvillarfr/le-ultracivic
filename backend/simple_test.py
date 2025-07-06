#!/usr/bin/env python3

import asyncio
from app.database import get_session
from app.models.allowances import Allowance, AllowanceStatus
from app.schemas.retirements import RetirementRequest
from sqlmodel import select
from uuid import uuid4

async def test_reservation_logic():
    """Test the core reservation logic without FastAPI"""
    
    print("Testing direct reservation logic...")
    
    # Test request
    retirement_request = RetirementRequest(
        num_allowances=1,
        message="Test message",
        wallet="0x742d35cc6634c0532925a3b8d11d2d7d2ae30b2b"
    )
    
    async for session in get_session():
        try:
            # Find and lock available allowances (same logic as in the API)
            stmt = (
                select(Allowance)
                .where(Allowance.status == AllowanceStatus.AVAILABLE)
                .limit(retirement_request.num_allowances)
                .with_for_update(skip_locked=True)
            )

            result = await session.execute(stmt)
            allowances = result.scalars().all()

            print(f"Found {len(allowances)} available allowances")

            if len(allowances) < retirement_request.num_allowances:
                print(f"❌ Only {len(allowances)} allowances available, but {retirement_request.num_allowances} requested")
                return False

            # Generate order ID and reserve allowances
            order_id = uuid4()
            print(f"Generated order ID: {order_id}")

            for allowance in allowances:
                print(f"Reserving allowance: {allowance.serial_number}")
                allowance.status = AllowanceStatus.RESERVED
                allowance.order_id = str(order_id)
                allowance.wallet = retirement_request.wallet
                allowance.message = retirement_request.message

            await session.commit()
            print("✅ Reservation successful!")
            return True
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Reservation failed: {str(e)}")
            return False
        finally:
            break

if __name__ == "__main__":
    print("=== Testing Reservation Logic ===")
    success = asyncio.run(test_reservation_logic())
    
    if success:
        print("🎉 The reservation logic is working correctly!")
    else:
        print("❌ There's still an issue with reservations")