"""Cleanup service for expired reservations and maintenance tasks."""

import logging
from datetime import datetime, timedelta
from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.config import settings
from app.database import get_session
from app.models.allowances import Allowance, AllowanceStatus

logger = logging.getLogger(__name__)


class CleanupService:
    """Service for cleaning up expired reservations and performing maintenance."""

    def __init__(self):
        self.reservation_timeout_minutes = settings.reservation_timeout_minutes

    async def cleanup_expired_reservations(self) -> Dict[str, any]:
        """
        Clean up reservations that have been reserved but not paid within the timeout period.
        
        Returns:
            Dict with cleanup results
        """
        try:
            cleanup_count = 0
            
            async for session in get_session():
                # Calculate timeout threshold
                timeout_threshold = datetime.utcnow() - timedelta(
                    minutes=self.reservation_timeout_minutes
                )
                
                # Find expired reservations
                stmt = select(Allowance).where(
                    Allowance.status == AllowanceStatus.RESERVED,
                    Allowance.timestamp < timeout_threshold
                )
                
                result = await session.execute(stmt)
                expired_allowances = result.scalars().all()
                
                if not expired_allowances:
                    logger.info("No expired reservations found")
                    return {
                        "success": True,
                        "cleaned_count": 0,
                        "message": "No expired reservations to clean"
                    }
                
                # Group by order_id for logging
                orders_cleaned = set()
                
                # Clean up expired allowances
                for allowance in expired_allowances:
                    orders_cleaned.add(allowance.order_id)
                    
                    # Reset allowance to available state
                    allowance.status = AllowanceStatus.AVAILABLE
                    allowance.order_id = None
                    allowance.wallet = None
                    allowance.message = None
                    allowance.tx_hash = None
                    allowance.reward_tx_hash = None
                    allowance.timestamp = None
                    allowance.updated_at = datetime.utcnow()
                    
                    cleanup_count += 1
                
                await session.commit()
                
                logger.info(
                    f"Cleaned up {cleanup_count} expired allowances from {len(orders_cleaned)} orders. "
                    f"Timeout threshold: {timeout_threshold}"
                )
                
                return {
                    "success": True,
                    "cleaned_count": cleanup_count,
                    "orders_cleaned": len(orders_cleaned),
                    "timeout_threshold": timeout_threshold.isoformat(),
                    "message": f"Cleaned {cleanup_count} expired allowances"
                }
                
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            return {
                "success": False,
                "error": f"Cleanup error: {str(e)}",
                "cleaned_count": 0
            }

    async def cleanup_orphaned_transactions(self) -> Dict[str, any]:
        """
        Clean up allowances that have transaction hashes but are stuck in processing.
        This handles cases where the transaction monitoring might have failed.
        
        Returns:
            Dict with cleanup results
        """
        try:
            cleanup_count = 0
            
            async for session in get_session():
                # Find allowances that have been in processing state too long
                # (have tx_hash but still reserved and older than 2x timeout)
                extended_timeout_threshold = datetime.utcnow() - timedelta(
                    minutes=self.reservation_timeout_minutes * 2
                )
                
                stmt = select(Allowance).where(
                    Allowance.status == AllowanceStatus.RESERVED,
                    Allowance.tx_hash.is_not(None),
                    Allowance.timestamp < extended_timeout_threshold
                )
                
                result = await session.execute(stmt)
                stuck_allowances = result.scalars().all()
                
                if not stuck_allowances:
                    logger.info("No stuck transactions found")
                    return {
                        "success": True,
                        "cleaned_count": 0,
                        "message": "No stuck transactions to clean"
                    }
                
                orders_cleaned = set()
                
                # Clean up stuck allowances
                for allowance in stuck_allowances:
                    orders_cleaned.add(allowance.order_id)
                    
                    # Reset allowance to available state
                    allowance.status = AllowanceStatus.AVAILABLE
                    allowance.order_id = None
                    allowance.wallet = None
                    allowance.message = None
                    allowance.tx_hash = None
                    allowance.reward_tx_hash = None
                    allowance.timestamp = None
                    allowance.updated_at = datetime.utcnow()
                    
                    cleanup_count += 1
                
                await session.commit()
                
                logger.warning(
                    f"Cleaned up {cleanup_count} stuck transaction allowances from {len(orders_cleaned)} orders. "
                    f"These were stuck in processing state beyond timeout."
                )
                
                return {
                    "success": True,
                    "cleaned_count": cleanup_count,
                    "orders_cleaned": len(orders_cleaned),
                    "timeout_threshold": extended_timeout_threshold.isoformat(),
                    "message": f"Cleaned {cleanup_count} stuck transaction allowances"
                }
                
        except Exception as e:
            logger.error(f"Error during orphaned transaction cleanup: {str(e)}")
            return {
                "success": False,
                "error": f"Orphaned cleanup error: {str(e)}",
                "cleaned_count": 0
            }

    async def get_cleanup_stats(self) -> Dict[str, any]:
        """
        Get statistics about reservations and potential cleanup candidates.
        
        Returns:
            Dict with current system stats
        """
        try:
            async for session in get_session():
                # Count total allowances by status
                available_stmt = select(Allowance).where(Allowance.status == AllowanceStatus.AVAILABLE)
                reserved_stmt = select(Allowance).where(Allowance.status == AllowanceStatus.RESERVED)
                retired_stmt = select(Allowance).where(Allowance.status == AllowanceStatus.RETIRED)
                
                available_result = await session.execute(available_stmt)
                reserved_result = await session.execute(reserved_stmt)
                retired_result = await session.execute(retired_stmt)
                
                available_count = len(available_result.scalars().all())
                reserved_count = len(reserved_result.scalars().all())
                retired_count = len(retired_result.scalars().all())
                
                # Count expired reservations
                timeout_threshold = datetime.utcnow() - timedelta(
                    minutes=self.reservation_timeout_minutes
                )
                
                expired_stmt = select(Allowance).where(
                    Allowance.status == AllowanceStatus.RESERVED,
                    Allowance.timestamp < timeout_threshold
                )
                
                expired_result = await session.execute(expired_stmt)
                expired_count = len(expired_result.scalars().all())
                
                # Count stuck transactions
                extended_timeout_threshold = datetime.utcnow() - timedelta(
                    minutes=self.reservation_timeout_minutes * 2
                )
                
                stuck_stmt = select(Allowance).where(
                    Allowance.status == AllowanceStatus.RESERVED,
                    Allowance.tx_hash.is_not(None),
                    Allowance.timestamp < extended_timeout_threshold
                )
                
                stuck_result = await session.execute(stuck_stmt)
                stuck_count = len(stuck_result.scalars().all())
                
                return {
                    "success": True,
                    "stats": {
                        "available_allowances": available_count,
                        "reserved_allowances": reserved_count,
                        "retired_allowances": retired_count,
                        "expired_reservations": expired_count,
                        "stuck_transactions": stuck_count,
                        "total_allowances": available_count + reserved_count + retired_count
                    },
                    "cleanup_thresholds": {
                        "reservation_timeout_minutes": self.reservation_timeout_minutes,
                        "next_cleanup_candidates": expired_count + stuck_count
                    }
                }
                
        except Exception as e:
            logger.error(f"Error getting cleanup stats: {str(e)}")
            return {
                "success": False,
                "error": f"Stats error: {str(e)}"
            }

    async def full_cleanup(self) -> Dict[str, any]:
        """
        Perform complete cleanup of expired reservations and stuck transactions.
        
        Returns:
            Dict with combined cleanup results
        """
        try:
            logger.info("Starting full cleanup process")
            
            # Cleanup expired reservations
            expired_result = await self.cleanup_expired_reservations()
            
            # Cleanup stuck transactions
            stuck_result = await self.cleanup_orphaned_transactions()
            
            total_cleaned = (
                expired_result.get("cleaned_count", 0) + 
                stuck_result.get("cleaned_count", 0)
            )
            
            result = {
                "success": expired_result["success"] and stuck_result["success"],
                "total_cleaned": total_cleaned,
                "expired_cleanup": expired_result,
                "stuck_cleanup": stuck_result,
                "message": f"Full cleanup completed. Total cleaned: {total_cleaned} allowances"
            }
            
            logger.info(f"Full cleanup completed: {total_cleaned} allowances cleaned")
            
            return result
            
        except Exception as e:
            logger.error(f"Error during full cleanup: {str(e)}")
            return {
                "success": False,
                "error": f"Full cleanup error: {str(e)}",
                "total_cleaned": 0
            }


# Global instance
cleanup_service = CleanupService()