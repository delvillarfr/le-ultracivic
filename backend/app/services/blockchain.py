"""Blockchain utilities and helper functions."""

import asyncio
import logging
from typing import Dict, List, Optional

from app.config import settings
from app.services.alchemy import alchemy_service
from app.services.thirdweb import thirdweb_service

logger = logging.getLogger(__name__)


class BlockchainService:
    """High-level blockchain service for coordinating operations."""

    def __init__(self):
        self.allowance_price_usd = settings.allowance_price_usd
        self.treasury_address = settings.treasury_wallet_address
        self.token_contract = settings.pr_token_contract_address

    async def process_payment_confirmation(
        self,
        tx_hash: str,
        order_id: str,
        num_allowances: int
    ) -> Dict[str, any]:
        """
        Process payment confirmation and initiate token transfer.
        
        Args:
            tx_hash: Payment transaction hash
            order_id: Order ID for the purchase
            num_allowances: Number of allowances purchased
            
        Returns:
            Dict with processing results
        """
        try:
            # Calculate expected payment amount
            expected_usd = num_allowances * self.allowance_price_usd
            # For now, assume 1 ETH = $2000 (should use 1inch for real price)
            expected_eth = expected_usd / 2000.0
            expected_wei = int(expected_eth * 10**18)
            
            # Verify the payment transaction
            verification = await alchemy_service.verify_payment_transaction(
                tx_hash=tx_hash,
                expected_to=self.treasury_address,
                min_value_wei=expected_wei
            )
            
            if not verification["valid"]:
                return {
                    "success": False,
                    "error": f"Payment verification failed: {verification['error']}",
                    "stage": "payment_verification"
                }
            
            logger.info(f"Payment verified for order {order_id}: {tx_hash}")
            
            return {
                "success": True,
                "payment_verified": True,
                "payment_amount_wei": verification["value_wei"],
                "block_number": verification["block_number"]
            }
            
        except Exception as e:
            logger.error(f"Error processing payment confirmation for {order_id}: {str(e)}")
            return {
                "success": False,
                "error": f"Payment processing error: {str(e)}",
                "stage": "processing"
            }

    async def distribute_reward_tokens(
        self,
        recipient_address: str,
        num_allowances: int,
        order_id: str
    ) -> Dict[str, any]:
        """
        Distribute $PR reward tokens to user.
        
        Args:
            recipient_address: User's wallet address
            num_allowances: Number of allowances (equals tokens to send)
            order_id: Order ID for tracking
            
        Returns:
            Dict with token transfer results
        """
        try:
            # Each allowance = 1 $PR token
            token_amount = num_allowances
            
            logger.info(f"Initiating token transfer for order {order_id}: {token_amount} tokens to {recipient_address}")
            
            # Initiate token transfer via Thirdweb
            transfer_result = await thirdweb_service.transfer_tokens(
                to_address=recipient_address,
                amount=token_amount
            )
            
            if not transfer_result["success"]:
                return {
                    "success": False,
                    "error": f"Token transfer failed: {transfer_result['error']}",
                    "stage": "token_transfer"
                }
            
            queue_id = transfer_result.get("queue_id")
            tx_hash = transfer_result.get("transaction_hash")
            
            logger.info(f"Token transfer initiated for order {order_id}: queue_id={queue_id}, tx_hash={tx_hash}")
            
            return {
                "success": True,
                "queue_id": queue_id,
                "transaction_hash": tx_hash,
                "token_amount": token_amount,
                "stage": "token_transfer_initiated"
            }
            
        except Exception as e:
            logger.error(f"Error distributing tokens for order {order_id}: {str(e)}")
            return {
                "success": False,
                "error": f"Token distribution error: {str(e)}",
                "stage": "token_distribution"
            }

    async def wait_for_token_transfer(
        self,
        queue_id: str,
        order_id: str,
        max_wait_seconds: int = 300
    ) -> Dict[str, any]:
        """
        Wait for token transfer to complete.
        
        Args:
            queue_id: Thirdweb queue ID
            order_id: Order ID for tracking
            max_wait_seconds: Maximum time to wait
            
        Returns:
            Dict with final transfer status
        """
        try:
            logger.info(f"Waiting for token transfer completion: order={order_id}, queue_id={queue_id}")
            
            result = await thirdweb_service.wait_for_transaction(
                queue_id=queue_id,
                max_wait_seconds=max_wait_seconds
            )
            
            if result["success"]:
                logger.info(f"Token transfer completed for order {order_id}: {result.get('transaction_hash')}")
            else:
                logger.error(f"Token transfer failed for order {order_id}: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error waiting for token transfer {order_id}: {str(e)}")
            return {
                "success": False,
                "error": f"Token transfer monitoring error: {str(e)}"
            }

    async def get_payment_status(self, tx_hash: str) -> Dict[str, any]:
        """
        Get current status of a payment transaction.
        
        Args:
            tx_hash: Transaction hash to check
            
        Returns:
            Dict with payment status
        """
        try:
            confirmed = await alchemy_service.is_transaction_confirmed(tx_hash)
            
            if confirmed is None:
                return {
                    "status": "pending",
                    "confirmed": False,
                    "message": "Transaction not yet confirmed"
                }
            elif confirmed:
                return {
                    "status": "confirmed",
                    "confirmed": True,
                    "message": "Payment confirmed successfully"
                }
            else:
                return {
                    "status": "failed",
                    "confirmed": False,
                    "message": "Payment transaction failed"
                }
                
        except Exception as e:
            logger.error(f"Error checking payment status for {tx_hash}: {str(e)}")
            return {
                "status": "error",
                "confirmed": False,
                "message": f"Error checking payment: {str(e)}"
            }

    async def estimate_gas_costs(self, num_allowances: int) -> Dict[str, any]:
        """
        Estimate gas costs for the complete transaction flow.
        
        Args:
            num_allowances: Number of allowances being purchased
            
        Returns:
            Dict with gas estimates
        """
        try:
            # Estimate gas for token transfer
            gas_estimate = await thirdweb_service.estimate_gas(
                to_address="0x0000000000000000000000000000000000000000",  # Placeholder
                amount=num_allowances
            )
            
            return {
                "success": True,
                "token_transfer_gas": gas_estimate.get("estimated_gas", 65000),
                "estimated_cost_wei": gas_estimate.get("estimated_cost_wei", "1300000000000000"),  # ~0.0013 ETH
                "estimated_cost_eth": "0.0013"
            }
            
        except Exception as e:
            logger.error(f"Error estimating gas costs: {str(e)}")
            return {
                "success": False,
                "error": f"Gas estimation error: {str(e)}"
            }


# Global instance
blockchain_service = BlockchainService()