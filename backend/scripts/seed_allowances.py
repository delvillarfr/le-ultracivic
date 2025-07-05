#!/usr/bin/env python3
"""
Database seeding script for Ultra Civic allowances table.
Populates the allowances table with serial numbers from allowances_available.csv.
"""

import asyncio
import csv
import logging
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.database import engine
from app.models.allowances import Allowance, AllowanceStatus
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import select

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
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


async def check_existing_allowances(session: AsyncSession) -> int:
    """Check if allowances already exist in the database"""
    stmt = select(Allowance)
    result = await session.execute(stmt)
    existing_count = len(result.scalars().all())
    return existing_count


async def seed_allowances(serial_numbers: List[str], session: AsyncSession) -> None:
    """Seed the allowances table with serial numbers"""
    logger.info(f"Seeding {len(serial_numbers)} allowances...")
    
    # Create allowance objects
    allowances = []
    for serial in serial_numbers:
        allowance = Allowance(
            serial_number=serial,
            status=AllowanceStatus.AVAILABLE,
            order_id=None,
            timestamp=None,
            wallet=None,
            message=None,
        )
        allowances.append(allowance)
    
    # Bulk insert
    try:
        session.add_all(allowances)
        await session.commit()
        logger.info(f"✅ Successfully seeded {len(allowances)} allowances")
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ Failed to seed allowances: {e}")
        raise


async def validate_seeded_data(session: AsyncSession, expected_count: int) -> None:
    """Validate that the seeded data is correct"""
    logger.info("Validating seeded data...")
    
    # Count total allowances
    stmt = select(Allowance)
    result = await session.execute(stmt)
    all_allowances = result.scalars().all()
    total_count = len(all_allowances)
    
    if total_count != expected_count:
        logger.error(f"❌ Expected {expected_count} allowances, found {total_count}")
        return False
    
    # Check all are available
    available_count = sum(1 for a in all_allowances if a.status == AllowanceStatus.AVAILABLE)
    if available_count != expected_count:
        logger.error(f"❌ Expected {expected_count} available allowances, found {available_count}")
        return False
    
    # Check for duplicates
    serial_numbers = [a.serial_number for a in all_allowances]
    unique_serials = set(serial_numbers)
    if len(unique_serials) != len(serial_numbers):
        logger.error(f"❌ Found duplicate serial numbers")
        return False
    
    logger.info(f"✅ Data validation passed: {total_count} unique available allowances")
    return True


async def main():
    """Main seeding function"""
    logger.info("Starting Ultra Civic allowances seeding...")
    
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
    
    # Create database session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Check if allowances already exist
        existing_count = await check_existing_allowances(session)
        
        if existing_count > 0:
            logger.warning(f"⚠️  Found {existing_count} existing allowances")
            response = input("Do you want to continue? This will add more allowances. (y/n): ")
            if response.lower() != 'y':
                logger.info("Seeding cancelled by user")
                return False
        
        # Seed the database
        await seed_allowances(serial_numbers, session)
        
        # Validate the seeded data
        total_expected = existing_count + len(serial_numbers)
        await validate_seeded_data(session, total_expected)
    
    logger.info("✅ Seeding completed successfully!")
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)