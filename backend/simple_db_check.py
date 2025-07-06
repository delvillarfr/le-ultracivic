#!/usr/bin/env python3
"""
Simple database check using the same pattern as the API
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import get_session
from app.models.allowances import Allowance, AllowanceStatus
from sqlmodel import select


async def simple_check():
    """Simple check using the same pattern as the API"""
    print("=== Simple Database Check ===")
    
    try:
        async for session in get_session():
            # Test the exact query from the API
            stmt = (
                select(Allowance)
                .where(Allowance.status == AllowanceStatus.AVAILABLE)
                .limit(5)
            )
            
            result = await session.execute(stmt)
            allowances = result.scalars().all()
            
            print(f"Found {len(allowances)} available allowances")
            
            for allowance in allowances:
                print(f"  - {allowance.serial_number}: {allowance.status}")
            
            if len(allowances) == 0:
                print("❌ NO AVAILABLE ALLOWANCES FOUND")
                print("   This explains the reservation timeout!")
                
                # Check if there are any allowances at all
                all_stmt = select(Allowance).limit(5)
                all_result = await session.execute(all_stmt)
                all_allowances = all_result.scalars().all()
                
                if len(all_allowances) == 0:
                    print("   Database is completely empty - need to run seeding script")
                else:
                    print(f"   Found {len(all_allowances)} total allowances (not available)")
                    for allowance in all_allowances:
                        print(f"   - {allowance.serial_number}: {allowance.status}")
                
                return False
            else:
                print("✅ Found available allowances - reservations should work")
                return True
            
            break  # Exit the async generator
            
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False


async def test_reservation_flow():
    """Test the exact reservation flow from the API"""
    print("\n=== Testing Reservation Flow ===")
    
    try:
        async for session in get_session():
            # Simulate the exact API flow
            num_allowances = 1
            
            # Step 1: Find and lock available allowances
            stmt = (
                select(Allowance)
                .where(Allowance.status == AllowanceStatus.AVAILABLE)
                .limit(num_allowances)
                .with_for_update(skip_locked=True)
            )
            
            result = await session.execute(stmt)
            allowances = result.scalars().all()
            
            print(f"Step 1: Found {len(allowances)} allowances to reserve")
            
            if len(allowances) < num_allowances:
                print(f"❌ Not enough allowances available ({len(allowances)} < {num_allowances})")
                return False
            
            # Step 2: Test the reservation (without actually committing)
            print("Step 2: Testing reservation logic")
            
            test_order_id = "test-order-123"
            test_wallet = "0x742d35cc6634c0532925a3b8d11d2d7d2ae30b2b"
            test_message = "Test message"
            
            for allowance in allowances:
                print(f"  Would reserve: {allowance.serial_number}")
                # Don't actually modify - just test the logic
                # allowance.status = AllowanceStatus.RESERVED
                # allowance.order_id = test_order_id
                # allowance.wallet = test_wallet
                # allowance.message = test_message
            
            # Don't commit - just test
            # await session.commit()
            
            print("✅ Reservation flow test successful")
            return True
            
            break  # Exit the async generator
            
    except Exception as e:
        print(f"❌ Reservation flow test failed: {e}")
        return False


async def main():
    """Main function"""
    print("Testing database for Ultra Civic reservation issues...")
    print("=" * 60)
    
    simple_ok = await simple_check()
    reservation_ok = await test_reservation_flow()
    
    print("\n" + "=" * 60)
    if simple_ok and reservation_ok:
        print("✅ DATABASE LOOKS HEALTHY!")
        print("   The reservation timeout issue is likely NOT database-related.")
        print("   Check:")
        print("   1. API endpoint timeout settings")
        print("   2. Network connectivity issues")
        print("   3. Database connection pooling")
        print("   4. Database locks or long-running transactions")
    else:
        print("❌ DATABASE ISSUES FOUND!")
        if not simple_ok:
            print("   → No available allowances - run seeding script")
        if not reservation_ok:
            print("   → Reservation query logic failing")
    
    return simple_ok and reservation_ok


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)