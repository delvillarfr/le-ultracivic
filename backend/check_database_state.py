#!/usr/bin/env python3
"""
Quick database inspection script to check allowances table state
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import get_session
from app.models.allowances import Allowance, AllowanceStatus
from sqlmodel import select, func


async def check_database_state():
    """Check the current state of the allowances table"""
    print("=== Database State Check ===")
    
    try:
        async for session in get_session():
            # Check if table exists and count total records
            try:
                total_count = await session.execute(
                    select(func.count(Allowance.serial_number))
                )
                total = total_count.scalar()
                print(f"Total allowances in database: {total}")
                
                if total == 0:
                    print("❌ DATABASE IS EMPTY - No allowances found!")
                    print("   This explains why reservations are timing out.")
                    print("   You need to run the seeding script.")
                    return False
                
                # Count by status
                for status in AllowanceStatus:
                    count_result = await session.execute(
                        select(func.count(Allowance.serial_number))
                        .where(Allowance.status == status)
                    )
                    count = count_result.scalar()
                    print(f"  {status.value}: {count}")
                
                # Show a few sample records
                print("\nSample records:")
                sample_result = await session.execute(
                    select(Allowance).limit(5)
                )
                samples = sample_result.scalars().all()
                
                for allowance in samples:
                    print(f"  {allowance.serial_number}: {allowance.status}")
                
                # Check for available allowances specifically
                available_count = await session.execute(
                    select(func.count(Allowance.serial_number))
                    .where(Allowance.status == AllowanceStatus.AVAILABLE)
                )
                available = available_count.scalar()
                
                if available == 0:
                    print("❌ NO AVAILABLE ALLOWANCES - All are reserved or retired!")
                    print("   This explains why reservations are failing.")
                    return False
                else:
                    print(f"✅ {available} allowances available for reservation")
                    return True
                    
            except Exception as e:
                print(f"❌ Error querying database: {e}")
                return False
            finally:
                break
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def test_reservation_query():
    """Test the exact query used in reservations"""
    print("\n=== Testing Reservation Query ===")
    
    try:
        async for session in get_session():
            # This is the exact query from the reservation endpoint
            stmt = (
                select(Allowance)
                .where(Allowance.status == AllowanceStatus.AVAILABLE)
                .limit(1)
                .with_for_update(skip_locked=True)
            )
            
            result = await session.execute(stmt)
            allowances = result.scalars().all()
            
            print(f"Reservation query found {len(allowances)} available allowances")
            
            if len(allowances) > 0:
                print("✅ Reservation query works correctly")
                for allowance in allowances:
                    print(f"  Available: {allowance.serial_number}")
                return True
            else:
                print("❌ Reservation query found no available allowances")
                return False
                
            break
            
    except Exception as e:
        print(f"❌ Reservation query failed: {e}")
        return False


async def main():
    """Main inspection function"""
    print("Checking database state for Ultra Civic allowances...")
    print("=" * 50)
    
    db_ok = await check_database_state()
    query_ok = await test_reservation_query()
    
    print("\n" + "=" * 50)
    if db_ok and query_ok:
        print("✅ Database looks healthy!")
        print("   The reservation timeout issue is likely elsewhere.")
    else:
        print("❌ Database issues found!")
        if not db_ok:
            print("   → Run the seeding script to populate allowances")
        if not query_ok:
            print("   → The reservation query is failing")
    
    return db_ok and query_ok


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)