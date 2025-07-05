"""Alchemy service for Ethereum blockchain interactions."""

import asyncio
import logging
from typing import Dict, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class AlchemyService:
    """Service for interacting with Alchemy API for transaction monitoring."""

    def __init__(self):
        self.api_url = settings.alchemy_sepolia_url
        self.timeout = httpx.Timeout(30.0)

    async def get_transaction_receipt(self, tx_hash: str) -> Optional[Dict]:
        """
        Get transaction receipt from Alchemy.
        
        Args:
            tx_hash: Transaction hash to check
            
        Returns:
            Transaction receipt dict or None if not found/pending
        """
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_getTransactionReceipt",
            "params": [tx_hash]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers
                )
                
                if response.status_code != 200:
                    logger.error(f"Alchemy API error: {response.status_code} - {response.text}")
                    return None
                
                data = response.json()
                
                if "error" in data:
                    logger.error(f"Alchemy RPC error: {data['error']}")
                    return None
                
                return data.get("result")
                
        except httpx.TimeoutException:
            logger.error(f"Timeout getting transaction receipt for {tx_hash}")
            return None
        except Exception as e:
            logger.error(f"Error getting transaction receipt for {tx_hash}: {str(e)}")
            return None

    async def is_transaction_confirmed(self, tx_hash: str) -> Optional[bool]:
        """
        Check if a transaction is confirmed on the blockchain.
        
        Args:
            tx_hash: Transaction hash to check
            
        Returns:
            True if confirmed, False if failed, None if pending or error
        """
        receipt = await self.get_transaction_receipt(tx_hash)
        
        if receipt is None:
            return None  # Transaction not found or still pending
        
        # Check transaction status (1 = success, 0 = failure)
        status = receipt.get("status")
        if status == "0x1":
            return True
        elif status == "0x0":
            return False
        else:
            logger.warning(f"Unknown transaction status for {tx_hash}: {status}")
            return None

    async def get_transaction_details(self, tx_hash: str) -> Optional[Dict]:
        """
        Get full transaction details including receipt and transaction data.
        
        Args:
            tx_hash: Transaction hash to check
            
        Returns:
            Dictionary with transaction details or None if error
        """
        # Get both transaction and receipt
        tasks = [
            self._get_transaction(tx_hash),
            self.get_transaction_receipt(tx_hash)
        ]
        
        try:
            transaction, receipt = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions from tasks
            if isinstance(transaction, Exception):
                logger.error(f"Error getting transaction {tx_hash}: {transaction}")
                transaction = None
                
            if isinstance(receipt, Exception):
                logger.error(f"Error getting receipt {tx_hash}: {receipt}")
                receipt = None
            
            return {
                "transaction": transaction,
                "receipt": receipt,
                "confirmed": receipt is not None,
                "successful": receipt and receipt.get("status") == "0x1" if receipt else None
            }
            
        except Exception as e:
            logger.error(f"Error getting transaction details for {tx_hash}: {str(e)}")
            return None

    async def _get_transaction(self, tx_hash: str) -> Optional[Dict]:
        """Get raw transaction data."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_getTransactionByHash",
            "params": [tx_hash]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers
                )
                
                if response.status_code != 200:
                    logger.error(f"Alchemy API error: {response.status_code} - {response.text}")
                    return None
                
                data = response.json()
                
                if "error" in data:
                    logger.error(f"Alchemy RPC error: {data['error']}")
                    return None
                
                return data.get("result")
                
        except Exception as e:
            logger.error(f"Error getting transaction {tx_hash}: {str(e)}")
            return None

    async def verify_payment_transaction(
        self, 
        tx_hash: str, 
        expected_to: str, 
        min_value_wei: int
    ) -> Dict[str, any]:
        """
        Verify a payment transaction meets requirements.
        
        Args:
            tx_hash: Transaction hash to verify
            expected_to: Expected recipient address (treasury)
            min_value_wei: Minimum value in wei
            
        Returns:
            Dict with verification results
        """
        details = await self.get_transaction_details(tx_hash)
        
        if not details:
            return {
                "valid": False,
                "error": "Could not retrieve transaction details"
            }
        
        transaction = details.get("transaction")
        receipt = details.get("receipt")
        
        if not transaction:
            return {
                "valid": False,
                "error": "Transaction not found"
            }
        
        if not receipt:
            return {
                "valid": False,
                "error": "Transaction not confirmed yet"
            }
        
        # Check if transaction was successful
        if receipt.get("status") != "0x1":
            return {
                "valid": False,
                "error": "Transaction failed"
            }
        
        # Check recipient
        tx_to = transaction.get("to", "").lower()
        if tx_to != expected_to.lower():
            return {
                "valid": False,
                "error": f"Incorrect recipient. Expected {expected_to}, got {tx_to}"
            }
        
        # Check value
        tx_value = int(transaction.get("value", "0"), 16)
        if tx_value < min_value_wei:
            return {
                "valid": False,
                "error": f"Insufficient payment. Expected at least {min_value_wei} wei, got {tx_value} wei"
            }
        
        return {
            "valid": True,
            "value_wei": tx_value,
            "block_number": int(receipt.get("blockNumber", "0"), 16),
            "gas_used": int(receipt.get("gasUsed", "0"), 16)
        }


# Global instance
alchemy_service = AlchemyService()