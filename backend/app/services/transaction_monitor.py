"""Transaction monitoring service for tracking blockchain payments."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.config import settings
from app.database import get_session
from app.models.allowances import Allowance, AllowanceStatus
from app.services.alchemy import alchemy_service
from app.services.blockchain import blockchain_service
from app.services.thirdweb import thirdweb_service

logger = logging.getLogger(__name__)


class TransactionMonitorService:
    """Service for monitoring pending transactions and processing payments."""

    def __init__(self):
        self.timeout_minutes = settings.tx_timeout_minutes
        self.check_interval = 10  # Check every 10 seconds
        self.max_retries = 3

    async def monitor_pending_transactions(self) -> None:
        """Monitor all pending transactions for confirmation."""
        try:
            async for session in get_session():
                # Find orders with tx_hash but still in reserved status
                stmt = select(Allowance).where(
                    Allowance.status == AllowanceStatus.RESERVED,
                    Allowance.tx_hash.is_not(None)
                ).distinct(Allowance.order_id)
                
                result = await session.execute(stmt)
                pending_orders = result.scalars().all()
                
                logger.info(f"Monitoring {len(pending_orders)} pending transactions")
                
                for allowance in pending_orders:
                    await self._process_pending_order(session, allowance)
                
                break  # Exit the async generator
                
        except Exception as e:
            logger.error(f"Error monitoring pending transactions: {str(e)}")

    async def _process_pending_order(
        self, 
        session: AsyncSession, 
        allowance: Allowance
    ) -> None:
        """Process a single pending order."""
        try:
            order_id = allowance.order_id
            tx_hash = allowance.tx_hash
            
            if not tx_hash:
                logger.warning(f"Order {order_id} has no tx_hash, skipping")
                return
            
            # Check if order has timed out
            if self._is_order_timed_out(allowance):
                logger.warning(f"Order {order_id} timed out, marking as failed")
                await self._mark_order_as_failed(session, order_id, "Payment timeout")
                return
            
            # Check transaction status
            is_confirmed = await alchemy_service.is_transaction_confirmed(tx_hash)
            
            if is_confirmed is None:
                # Still pending, continue monitoring
                logger.debug(f"Order {order_id} transaction {tx_hash} still pending")
                return
            elif is_confirmed is False:
                # Transaction failed
                logger.error(f"Order {order_id} transaction {tx_hash} failed")
                await self._mark_order_as_failed(session, order_id, "Payment transaction failed")
                return
            elif is_confirmed is True:
                # Transaction confirmed, process payment
                logger.info(f"Order {order_id} transaction {tx_hash} confirmed, processing payment")
                await self._process_confirmed_payment(session, order_id)
                return
                
        except Exception as e:
            logger.error(f"Error processing pending order {allowance.order_id}: {str(e)}")

    async def _process_confirmed_payment(
        self, 
        session: AsyncSession, 
        order_id: str
    ) -> None:
        """Process a confirmed payment by distributing tokens and retiring allowances."""
        try:
            # Get all allowances for this order
            stmt = select(Allowance).where(Allowance.order_id == order_id)
            result = await session.execute(stmt)
            allowances = result.scalars().all()
            
            if not allowances:
                logger.error(f"No allowances found for order {order_id}")
                return
            
            first_allowance = allowances[0]
            num_allowances = len(allowances)
            wallet_address = first_allowance.wallet
            
            if not wallet_address:
                logger.error(f"No wallet address for order {order_id}")
                await self._mark_order_as_failed(session, order_id, "Missing wallet address")
                return
            
            # Distribute reward tokens
            logger.info(f"Distributing {num_allowances} tokens to {wallet_address} for order {order_id}")
            
            token_result = await thirdweb_service.transfer_tokens(
                to_address=wallet_address,
                amount=num_allowances
            )
            
            if not token_result["success"]:
                logger.error(f"Token transfer failed for order {order_id}: {token_result.get('error')}")
                
                # Send email alert for token transfer failure
                try:
                    from app.services.email import email_service
                    await email_service.send_token_transfer_failure_alert(
                        order_id=order_id,
                        wallet_address=wallet_address,
                        num_allowances=num_allowances,
                        error_details=token_result.get('error', 'Unknown error'),
                        thirdweb_response=token_result
                    )
                except Exception as email_error:
                    logger.error(f"Failed to send token transfer failure alert: {email_error}")
                
                await self._mark_order_as_failed(session, order_id, f"Token transfer failed: {token_result.get('error')}")
                return
            
            # Wait for token transfer to complete
            queue_id = token_result.get("queue_id")
            if queue_id:
                logger.info(f"Waiting for token transfer completion for order {order_id}")
                wait_result = await thirdweb_service.wait_for_transaction(
                    queue_id=queue_id,
                    max_wait_seconds=300  # 5 minutes
                )
                
                if not wait_result["success"]:
                    logger.error(f"Token transfer wait failed for order {order_id}: {wait_result.get('error')}")
                    
                    # Send email alert for token transfer wait failure
                    try:
                        from app.services.email import email_service
                        await email_service.send_token_transfer_failure_alert(
                            order_id=order_id,
                            wallet_address=wallet_address,
                            num_allowances=num_allowances,
                            error_details=f"Token transfer wait failed: {wait_result.get('error')}",
                            thirdweb_response=wait_result
                        )
                    except Exception as email_error:
                        logger.error(f"Failed to send token transfer wait failure alert: {email_error}")
                    
                    await self._mark_order_as_failed(session, order_id, f"Token transfer incomplete: {wait_result.get('error')}")
                    return
                
                reward_tx_hash = wait_result.get("transaction_hash")
            else:
                reward_tx_hash = token_result.get("transaction_hash")
            
            # Mark allowances as retired and store reward transaction hash
            for allowance in allowances:
                allowance.status = AllowanceStatus.RETIRED
                allowance.reward_tx_hash = reward_tx_hash
                allowance.updated_at = datetime.utcnow()
            
            await session.commit()
            
            logger.info(f"Order {order_id} completed successfully. Allowances retired, tokens distributed.")
            
        except Exception as e:
            logger.error(f"Error processing confirmed payment for order {order_id}: {str(e)}")
            await session.rollback()
            await self._mark_order_as_failed(session, order_id, f"Processing error: {str(e)}")

    async def _mark_order_as_failed(
        self, 
        session: AsyncSession, 
        order_id: str, 
        reason: str
    ) -> None:
        """Mark an order as failed and release the allowances."""
        try:
            # Get all allowances for this order
            stmt = select(Allowance).where(Allowance.order_id == order_id)
            result = await session.execute(stmt)
            allowances = result.scalars().all()
            
            # Release allowances back to available
            for allowance in allowances:
                allowance.status = AllowanceStatus.AVAILABLE
                allowance.order_id = None
                allowance.wallet = None
                allowance.message = None
                allowance.tx_hash = None
                allowance.reward_tx_hash = None
                allowance.updated_at = datetime.utcnow()
            
            await session.commit()
            
            logger.info(f"Order {order_id} marked as failed and allowances released. Reason: {reason}")
            
        except Exception as e:
            logger.error(f"Error marking order {order_id} as failed: {str(e)}")
            await session.rollback()

    def _is_order_timed_out(self, allowance: Allowance) -> bool:
        """Check if an order has timed out."""
        if not allowance.timestamp:
            return False
        
        timeout_threshold = datetime.utcnow() - timedelta(minutes=self.timeout_minutes)
        return allowance.timestamp < timeout_threshold

    async def process_single_order(self, order_id: str) -> Dict[str, any]:
        """Process a single order manually (for testing or immediate processing)."""
        try:
            async for session in get_session():
                stmt = select(Allowance).where(Allowance.order_id == order_id)
                result = await session.execute(stmt)
                allowances = result.scalars().all()
                
                if not allowances:
                    return {
                        "success": False,
                        "error": f"Order {order_id} not found"
                    }
                
                first_allowance = allowances[0]
                
                if first_allowance.status != AllowanceStatus.RESERVED:
                    return {
                        "success": False,
                        "error": f"Order {order_id} is not in reserved status"
                    }
                
                if not first_allowance.tx_hash:
                    return {
                        "success": False,
                        "error": f"Order {order_id} has no transaction hash"
                    }
                
                await self._process_pending_order(session, first_allowance)
                
                return {
                    "success": True,
                    "message": f"Order {order_id} processed"
                }
                
        except Exception as e:
            logger.error(f"Error processing single order {order_id}: {str(e)}")
            return {
                "success": False,
                "error": f"Processing error: {str(e)}"
            }


# Global instance
transaction_monitor = TransactionMonitorService()