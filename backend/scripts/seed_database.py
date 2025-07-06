#!/usr/bin/env python3
"""
Production-ready database seeding script for Ultra Civic allowances.
Use this script to populate the database with the actual allowances data.
"""

import asyncio
import csv
import logging
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_csv_ranges(csv_file_path: str) -> List[Tuple[int, int, str, str]]:
    """Parse CSV file and extract serial number ranges"""
    ranges = []
    
    with open(csv_file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            serial_range = row['Serial Range'].strip()
            state = row['Originating State'].strip()
            year = row['Allocation Year'].strip()
            
            # Parse the range "start - end"
            match = re.match(r'(\d+) - (\d+)', serial_range)
            if match:
                start = int(match.group(1))
                end = int(match.group(2))
                ranges.append((start, end, state, year))
            else:
                logger.warning(f"Could not parse range: {serial_range}")
    
    return ranges


def generate_serial_numbers(ranges: List[Tuple[int, int, str, str]]) -> List[str]:
    """Generate all individual serial numbers from ranges"""
    all_serials = []
    
    for start, end, state, year in ranges:
        count = end - start + 1
        logger.info(f"Generating {count} serials for {state} {year}: {start}-{end}")
        
        for serial in range(start, end + 1):
            all_serials.append(str(serial))
    
    return all_serials


async def seed_database_with_raw_sql(database_url: str, serial_numbers: List[str]) -> bool:
    """Seed the database using raw SQL for better performance"""
    try:
        import asyncpg
        
        # Connect to database
        conn = await asyncpg.connect(database_url)
        
        # Check if table exists and has data
        existing_count = await conn.fetchval(
            "SELECT COUNT(*) FROM allowances"
        )
        
        if existing_count > 0:
            logger.warning(f"Found {existing_count} existing allowances in database")
            response = input("Continue? This will add more allowances (y/n): ")
            if response.lower() != 'y':
                await conn.close()
                return False
        
        # Prepare batch insert data
        logger.info(f"Preparing to insert {len(serial_numbers)} allowances...")
        
        # Create the SQL and data for batch insert
        insert_sql = """
            INSERT INTO allowances (serial_number, status, created_at, updated_at)
            VALUES ($1, $2, NOW(), NOW())
            ON CONFLICT (serial_number) DO NOTHING
        """
        
        # Execute batch insert
        batch_data = [(serial, 'AVAILABLE') for serial in serial_numbers]
        
        async with conn.transaction():
            await conn.executemany(insert_sql, batch_data)
        
        # Verify insertion
        final_count = await conn.fetchval(
            "SELECT COUNT(*) FROM allowances WHERE status = 'AVAILABLE'"
        )
        
        await conn.close()
        
        logger.info(f"✅ Successfully seeded database")
        logger.info(f"Total available allowances: {final_count}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database seeding failed: {e}")
        return False


async def main():
    """Main seeding function"""
    logger.info("Starting Ultra Civic allowances database seeding...")
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("❌ DATABASE_URL environment variable not set")
        return False
    
    # Path to CSV file
    csv_file_path = Path(__file__).parent.parent / "allowances_available.csv"
    
    if not csv_file_path.exists():
        logger.error(f"❌ CSV file not found: {csv_file_path}")
        return False
    
    # Parse CSV ranges
    logger.info(f"Parsing CSV file: {csv_file_path}")
    ranges = parse_csv_ranges(str(csv_file_path))
    logger.info(f"Found {len(ranges)} ranges in CSV")
    
    # Generate serial numbers
    serial_numbers = generate_serial_numbers(ranges)
    logger.info(f"Generated {len(serial_numbers)} unique serial numbers")
    
    if len(serial_numbers) != 999:
        logger.error(f"❌ Expected 999 serial numbers, got {len(serial_numbers)}")
        return False
    
    # Seed the database
    success = await seed_database_with_raw_sql(database_url, serial_numbers)
    
    if success:
        logger.info("✅ Database seeding completed successfully!")
    else:
        logger.error("❌ Database seeding failed!")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)