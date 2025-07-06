#!/usr/bin/env python3
"""
Debug the specific timeout issue with the reservation endpoint
"""

import asyncio
import time
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import get_session
from app.models.allowances import Allowance, AllowanceStatus
from app.schemas.retirements import RetirementRequest
from sqlmodel import select
from uuid import uuid4


async def test_timeout_scenario():
    """Test the exact scenario causing timeouts"""
    print("=== Testing Timeout Scenario ===")
    
    # Create test request
    retirement_request = RetirementRequest(
        num_allowances=1,
        message="Timeout test message",
        wallet="0x742d35cc6634c0532925a3b8d11d2d7d2ae30b2b"
    )
    
    print(f"Testing reservation for {retirement_request.num_allowances} allowances...")
    
    try:
        start_time = time.time()
        
        async for session in get_session():
            print(f"Step 1: Got database session ({time.time() - start_time:.2f}s)")
            
            # This is the exact query from the API
            stmt = (
                select(Allowance)
                .where(Allowance.status == AllowanceStatus.AVAILABLE)
                .limit(retirement_request.num_allowances)
                .with_for_update(skip_locked=True)
            )
            
            print(f"Step 2: Executing query ({time.time() - start_time:.2f}s)")
            result = await session.execute(stmt)
            
            print(f"Step 3: Got query result ({time.time() - start_time:.2f}s)")
            allowances = result.scalars().all()
            
            print(f"Step 4: Found {len(allowances)} allowances ({time.time() - start_time:.2f}s)")
            
            if len(allowances) < retirement_request.num_allowances:
                print(f"❌ Not enough allowances: {len(allowances)} < {retirement_request.num_allowances}")
                return False
            
            # Generate order ID
            order_id = uuid4()
            print(f"Step 5: Generated order ID: {order_id} ({time.time() - start_time:.2f}s)")
            
            # Update allowances
            for i, allowance in enumerate(allowances):
                print(f"Step 6.{i+1}: Updating allowance {allowance.serial_number} ({time.time() - start_time:.2f}s)")
                allowance.status = AllowanceStatus.RESERVED
                allowance.order_id = str(order_id)
                allowance.wallet = retirement_request.wallet
                allowance.message = retirement_request.message
            
            print(f"Step 7: Committing transaction ({time.time() - start_time:.2f}s)")
            await session.commit()
            
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"✅ SUCCESS! Total time: {total_time:.2f}s")
            
            if total_time > 10:
                print("⚠️  WARNING: Operation took more than 10 seconds!")
            elif total_time > 5:
                print("⚠️  WARNING: Operation took more than 5 seconds!")
            else:
                print("✅ Operation completed in reasonable time")
            
            return True
            
            break  # Exit the async generator
            
    except Exception as e:
        end_time = time.time()
        total_time = end_time - start_time
        print(f"❌ ERROR after {total_time:.2f}s: {str(e)}")
        return False


async def test_database_locks():
    """Test if there are any database locks causing issues"""
    print("\n=== Testing Database Locks ===")
    
    try:
        async for session in get_session():
            # Check for locks
            lock_query = """
            SELECT 
                pid,
                usename,
                query,
                state,
                query_start,
                state_change
            FROM pg_stat_activity 
            WHERE state = 'active' 
            AND query NOT LIKE '%pg_stat_activity%'
            ORDER BY query_start;
            """
            
            from sqlalchemy import text
            result = await session.execute(text(lock_query))
            locks = result.fetchall()
            
            if locks:
                print(f"Found {len(locks)} active database sessions:")
                for lock in locks:
                    print(f"  PID {lock[0]}: {lock[1]} - {lock[2][:100]}...")
            else:
                print("✅ No active database sessions found")
            
            # Check for table locks specifically
            table_lock_query = """
            SELECT 
                l.mode,
                l.granted,
                a.query,
                a.pid,
                a.usename
            FROM pg_locks l
            JOIN pg_stat_activity a ON l.pid = a.pid
            WHERE l.relation = 'allowances'::regclass
            AND a.query NOT LIKE '%pg_stat_activity%'
            ORDER BY l.granted DESC;
            """
            
            result = await session.execute(text(table_lock_query))
            table_locks = result.fetchall()
            
            if table_locks:
                print(f"Found {len(table_locks)} locks on allowances table:")
                for lock in table_locks:
                    status = "GRANTED" if lock[1] else "WAITING"
                    print(f"  {lock[0]} ({status}): PID {lock[3]} - {lock[2][:100]}...")
            else:
                print("✅ No locks on allowances table")
                
            break
            
    except Exception as e:
        print(f"❌ Error checking locks: {str(e)}")
        return False
    
    return True


async def test_concurrent_access():
    """Test what happens with concurrent access"""
    print("\n=== Testing Concurrent Access ===")
    
    async def single_reservation(session_id):
        """Simulate a single reservation"""
        try:
            async for session in get_session():
                print(f"Session {session_id}: Starting reservation")
                
                stmt = (
                    select(Allowance)
                    .where(Allowance.status == AllowanceStatus.AVAILABLE)
                    .limit(1)
                    .with_for_update(skip_locked=True)
                )
                
                result = await session.execute(stmt)
                allowances = result.scalars().all()
                
                if len(allowances) > 0:
                    print(f"Session {session_id}: Found allowance {allowances[0].serial_number}")
                    # Simulate some processing time
                    await asyncio.sleep(0.1)
                    print(f"Session {session_id}: Completed")
                else:
                    print(f"Session {session_id}: No allowances found")
                
                break
                
        except Exception as e:
            print(f"Session {session_id}: Error - {str(e)}")
    
    # Run 3 concurrent reservation attempts
    tasks = []
    for i in range(3):
        task = asyncio.create_task(single_reservation(i+1))
        tasks.append(task)
    
    await asyncio.gather(*tasks)
    print("✅ Concurrent access test completed")


async def main():
    """Main debug function"""
    print("Debugging Ultra Civic reservation timeout issue...")
    print("=" * 60)
    
    # Test 1: Basic timeout scenario
    timeout_ok = await test_timeout_scenario()
    
    # Test 2: Database locks
    lock_ok = await test_database_locks()
    
    # Test 3: Concurrent access
    await test_concurrent_access()
    
    print("\n" + "=" * 60)
    print("DIAGNOSIS:")
    
    if timeout_ok:
        print("✅ Reservation logic works correctly")
        print("   → The timeout issue is likely NOT in the database logic")
        print("   → Check frontend timeout settings")
        print("   → Check network connectivity")
        print("   → Check if backend server is running correctly")
    else:
        print("❌ Reservation logic has issues")
        print("   → Database query or transaction problems")
        print("   → Possible deadlock or lock contention")
    
    if lock_ok:
        print("✅ No obvious database lock issues")
    else:
        print("❌ Database lock issues detected")
        
    print("\nRECOMMENDATIONS:")
    print("1. Check if backend server is running: python -m uvicorn app.main:app --port 8000")
    print("2. Test the manual reservation script: python manual_test_fix.py")
    print("3. Check frontend timeout settings in api.ts")
    print("4. Monitor database performance during reservations")
    
    return timeout_ok


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)