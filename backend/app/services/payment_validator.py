"""Payment validation service for enhanced payment confirmation."""

import logging
from typing import Dict, Optional

from app.config import settings
from app.services.alchemy import alchemy_service
from app.services.price_service import price_service

logger = logging.getLogger(__name__)


class PaymentValidator:
    """Service for validating payments with real-time verification."""

    def __init__(self):
        self.treasury_address = settings.treasury_wallet_address
        self.min_confirmations = settings.min_confirmations
        self.max_retries = settings.max_payment_retries

    async def validate_transaction_hash(self, tx_hash: str) -> Dict[str, any]:
        """
        Validate transaction hash format and existence.
        
        Args:
            tx_hash: Transaction hash to validate
            
        Returns:
            Dict with validation result
        """
        try:
            # Check format
            if not tx_hash.startswith("0x") or len(tx_hash) != 66:
                return {
                    "success": False,
                    "valid": False,
                    "error": "Invalid transaction hash format",
                    "details": {
                        "expected_format": "0x followed by 64 hexadecimal characters",
                        "received_length": len(tx_hash),
                        "received_format": tx_hash[:10] + "..." if len(tx_hash) > 10 else tx_hash
                    }
                }
            
            # Check if transaction exists
            transaction_details = await alchemy_service.get_transaction_details(tx_hash)
            
            if not transaction_details:
                return {
                    "success": False,
                    "valid": False,
                    "error": "Transaction not found on blockchain",
                    "details": {
                        "tx_hash": tx_hash,
                        "network": "Sepolia testnet"
                    }
                }
            
            transaction = transaction_details.get("transaction")
            receipt = transaction_details.get("receipt")
            
            if not transaction:
                return {
                    "success": False,
                    "valid": False,
                    "error": "Transaction details not available",
                    "details": {
                        "tx_hash": tx_hash,
                        "status": "transaction_not_found"
                    }
                }
            
            return {
                "success": True,
                "valid": True,
                "message": "Transaction hash is valid and exists",
                "details": {
                    "tx_hash": tx_hash,
                    "transaction_exists": True,
                    "has_receipt": receipt is not None,
                    "confirmed": transaction_details.get("confirmed", False),
                    "successful": transaction_details.get("successful")
                }
            }
            
        except Exception as e:
            logger.error(f"Error validating transaction hash {tx_hash}: {str(e)}")
            return {
                "success": False,
                "error": f"Transaction validation error: {str(e)}"
            }

    async def validate_payment_transaction(
        self, 
        tx_hash: str, 
        num_allowances: int
    ) -> Dict[str, any]:
        """
        Comprehensive payment transaction validation.
        
        Args:
            tx_hash: Transaction hash to validate
            num_allowances: Number of allowances being purchased
            
        Returns:
            Dict with complete validation result
        """
        try:
            # Step 1: Validate transaction hash format and existence
            tx_validation = await self.validate_transaction_hash(tx_hash)
            
            if not tx_validation["success"] or not tx_validation["valid"]:
                return tx_validation
            
            # Step 2: Get transaction details
            transaction_details = await alchemy_service.get_transaction_details(tx_hash)
            
            if not transaction_details:
                return {
                    "success": False,
                    "valid": False,
                    "error": "Unable to retrieve transaction details"
                }
            
            transaction = transaction_details.get("transaction")
            receipt = transaction_details.get("receipt")
            
            # Step 3: Check if transaction is confirmed
            if not receipt:
                return {
                    "success": True,
                    "valid": False,
                    "status": "pending",
                    "message": "Transaction is pending confirmation",
                    "details": {
                        "tx_hash": tx_hash,
                        "confirmations": 0,
                        "required_confirmations": self.min_confirmations
                    }
                }
            
            # Step 4: Check if transaction was successful
            if receipt.get("status") != "0x1":
                return {
                    "success": False,
                    "valid": False,
                    "error": "Transaction failed on blockchain",
                    "details": {
                        "tx_hash": tx_hash,
                        "status": receipt.get("status"),
                        "block_number": receipt.get("blockNumber")
                    }
                }
            
            # Step 5: Validate recipient address
            tx_to = transaction.get("to", "").lower()
            if tx_to != self.treasury_address.lower():
                return {
                    "success": False,
                    "valid": False,
                    "error": "Incorrect recipient address",
                    "details": {
                        "expected_recipient": self.treasury_address,
                        "actual_recipient": transaction.get("to"),
                        "tx_hash": tx_hash
                    }
                }
            
            # Step 6: Validate payment amount
            payment_amount_wei = int(transaction.get("value", "0"), 16)
            
            amount_validation = await price_service.validate_payment_amount(
                num_allowances=num_allowances,
                payment_amount_wei=payment_amount_wei
            )
            
            if not amount_validation["success"] or not amount_validation.get("valid", False):
                return {
                    "success": False,
                    "valid": False,
                    "error": "Payment amount validation failed",
                    "details": amount_validation.get("details", {}),
                    "amount_error": amount_validation.get("error")
                }
            
            # Step 7: All validations passed
            return {
                "success": True,
                "valid": True,
                "message": "Payment transaction is valid and confirmed",
                "payment_details": {
                    "tx_hash": tx_hash,
                    "recipient": tx_to,
                    "amount_wei": payment_amount_wei,
                    "amount_eth": payment_amount_wei / 10**18,
                    "block_number": int(receipt.get("blockNumber", "0"), 16),
                    "gas_used": int(receipt.get("gasUsed", "0"), 16),
                    "confirmations": "confirmed",
                    "num_allowances": num_allowances
                },
                "price_validation": amount_validation
            }
            
        except Exception as e:
            logger.error(f"Error validating payment transaction {tx_hash}: {str(e)}")
            return {
                "success": False,
                "error": f"Payment validation error: {str(e)}"
            }

    async def quick_payment_check(self, tx_hash: str) -> Dict[str, any]:
        """
        Quick payment status check without full validation.
        
        Args:
            tx_hash: Transaction hash to check
            
        Returns:
            Dict with quick status check
        """
        try:
            # Check if transaction is confirmed
            is_confirmed = await alchemy_service.is_transaction_confirmed(tx_hash)
            
            if is_confirmed is None:
                return {
                    "success": True,
                    "status": "pending",
                    "message": "Transaction is pending confirmation"
                }
            elif is_confirmed is False:
                return {
                    "success": False,
                    "status": "failed",
                    "message": "Transaction failed on blockchain"
                }
            else:
                return {
                    "success": True,
                    "status": "confirmed",
                    "message": "Transaction is confirmed"
                }
                
        except Exception as e:
            logger.error(f"Error in quick payment check for {tx_hash}: {str(e)}")
            return {
                "success": False,
                "error": f"Quick check error: {str(e)}"
            }

    async def estimate_confirmation_time(self, tx_hash: str) -> Dict[str, any]:
        """
        Estimate confirmation time for a pending transaction.
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Dict with confirmation estimate
        """
        try:
            transaction_details = await alchemy_service.get_transaction_details(tx_hash)
            
            if not transaction_details:
                return {
                    "success": False,
                    "error": "Transaction not found"
                }
            
            transaction = transaction_details.get("transaction")
            receipt = transaction_details.get("receipt")
            
            if receipt:
                return {
                    "success": True,
                    "status": "confirmed",
                    "message": "Transaction is already confirmed"
                }
            
            # For Sepolia testnet, blocks are ~12 seconds
            # With 1 confirmation requirement, should be confirmed within ~30 seconds
            estimated_seconds = 30
            
            return {
                "success": True,
                "status": "pending",
                "estimated_confirmation_seconds": estimated_seconds,
                "estimated_confirmation_text": f"~{estimated_seconds} seconds",
                "network": "Sepolia testnet",
                "required_confirmations": self.min_confirmations
            }
            
        except Exception as e:
            logger.error(f"Error estimating confirmation time for {tx_hash}: {str(e)}")
            return {
                "success": False,
                "error": f"Estimation error: {str(e)}"
            }


# Global instance
payment_validator = PaymentValidator()