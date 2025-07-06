#!/usr/bin/env python3
"""
Simple database connection test
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.database import engine
import asyncpg


async def test_sqlalchemy_connection():
    """Test SQLAlchemy engine connection"""
    print("=== Testing SQLAlchemy Connection ===")
    
    try:
        # Test the engine connection
        from sqlalchemy import text
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"✅ SQLAlchemy connection successful: {row}")
            return True
            
    except Exception as e:
        print(f"❌ SQLAlchemy connection failed: {e}")
        return False


async def test_direct_asyncpg_connection():
    """Test direct asyncpg connection"""
    print("\n=== Testing Direct asyncpg Connection ===")
    
    try:
        # Convert SQLAlchemy URL to asyncpg format
        db_url = settings.database_url
        if db_url.startswith("postgresql+asyncpg://"):
            db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
        
        conn = await asyncpg.connect(db_url)
        result = await conn.fetchval("SELECT 1")
        await conn.close()
        
        print(f"✅ Direct asyncpg connection successful: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Direct asyncpg connection failed: {e}")
        return False


async def test_table_existence():
    """Test if allowances table exists"""
    print("\n=== Testing Table Existence ===")
    
    try:
        from sqlalchemy import text
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'allowances'
                )
            """))
            exists = result.fetchone()[0]
            
            if exists:
                print("✅ allowances table exists")
                return True
            else:
                print("❌ allowances table does NOT exist")
                return False
                
    except Exception as e:
        print(f"❌ Table existence check failed: {e}")
        return False


async def main():
    """Main connection test"""
    print("Testing database connectivity...")
    print("=" * 50)
    print(f"Database URL: {settings.database_url[:50]}...")
    
    sqlalchemy_ok = await test_sqlalchemy_connection()
    asyncpg_ok = await test_direct_asyncpg_connection()
    table_ok = await test_table_existence()
    
    print("\n" + "=" * 50)
    if sqlalchemy_ok and asyncpg_ok and table_ok:
        print("✅ All database tests passed!")
        print("   Database connection is healthy.")
    else:
        print("❌ Some database tests failed!")
        if not sqlalchemy_ok:
            print("   → SQLAlchemy connection issue")
        if not asyncpg_ok:
            print("   → asyncpg connection issue")
        if not table_ok:
            print("   → allowances table missing - run migrations")
    
    return sqlalchemy_ok and asyncpg_ok and table_ok


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)