"""Thirdweb service for token transfers and smart contract interactions."""

import logging
from typing import Dict, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class ThirdwebService:
    """Service for interacting with Thirdweb Engine API for token transfers."""

    def __init__(self):
        self.base_url = "https://engine.thirdweb.com"
        self.secret_key = settings.thirdweb_secret_key
        self.chain_id = "11155111"  # Sepolia testnet
        self.timeout = httpx.Timeout(60.0)  # Token transfers can take time

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Thirdweb API requests."""
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }

    async def transfer_tokens(
        self,
        to_address: str,
        amount: int,
        from_address: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Transfer ERC-20 tokens using Thirdweb Engine.
        
        Args:
            to_address: Recipient wallet address
            amount: Amount of tokens to transfer (in smallest unit)
            from_address: Sender address (defaults to treasury)
            
        Returns:
            Dict with transfer result and transaction hash
        """
        if from_address is None:
            from_address = settings.treasury_wallet_address
        
        url = f"{self.base_url}/contract/{self.chain_id}/{settings.pr_token_contract_address}/erc20/transfer"
        
        payload = {
            "toAddress": to_address,
            "amount": str(amount)
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "transaction_hash": data.get("result", {}).get("transactionHash"),
                        "queue_id": data.get("result", {}).get("queueId"),
                        "data": data
                    }
                else:
                    error_msg = f"Thirdweb API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    
                    # Send email alert for token transfer failure
                    try:
                        from app.services.email import email_service
                        await email_service.send_token_transfer_failure_alert(
                            order_id="unknown",
                            wallet_address=to_address,
                            num_allowances=amount // (10**18),  # Rough estimate
                            error_details=error_msg,
                            thirdweb_response=response.text
                        )
                    except Exception as email_error:
                        logger.error(f"Failed to send email alert: {email_error}")
                    
                    return {
                        "success": False,
                        "error": error_msg,
                        "status_code": response.status_code
                    }
                    
        except httpx.TimeoutException:
            error_msg = f"Timeout transferring tokens to {to_address}"
            logger.error(error_msg)
            
            # Send email alert for timeout
            try:
                from app.services.email import email_service
                await email_service.send_token_transfer_failure_alert(
                    order_id="unknown",
                    wallet_address=to_address,
                    num_allowances=amount // (10**18),  # Rough estimate
                    error_details=error_msg,
                    thirdweb_response={"error": "timeout"}
                )
            except Exception as email_error:
                logger.error(f"Failed to send email alert: {email_error}")
            
            return {
                "success": False,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Error transferring tokens to {to_address}: {str(e)}"
            logger.error(error_msg)
            
            # Send email alert for general errors
            try:
                from app.services.email import email_service
                await email_service.send_token_transfer_failure_alert(
                    order_id="unknown",
                    wallet_address=to_address,
                    num_allowances=amount // (10**18),  # Rough estimate
                    error_details=error_msg,
                    thirdweb_response={"error": str(e)}
                )
            except Exception as email_error:
                logger.error(f"Failed to send email alert: {email_error}")
            
            return {
                "success": False,
                "error": error_msg
            }

    async def get_transaction_status(self, queue_id: str) -> Dict[str, any]:
        """
        Get the status of a queued transaction.
        
        Args:
            queue_id: Queue ID from Thirdweb transaction
            
        Returns:
            Dict with transaction status
        """
        url = f"{self.base_url}/transaction/status/{queue_id}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    result = data.get("result", {})
                    
                    return {
                        "success": True,
                        "status": result.get("status"),  # "queued", "sent", "mined", "errored"
                        "transaction_hash": result.get("transactionHash"),
                        "error_message": result.get("errorMessage"),
                        "data": data
                    }
                else:
                    error_msg = f"Thirdweb status API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "error": error_msg
                    }
                    
        except Exception as e:
            error_msg = f"Error getting transaction status for {queue_id}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    async def get_token_balance(self, wallet_address: str) -> Dict[str, any]:
        """
        Get ERC-20 token balance for a wallet.
        
        Args:
            wallet_address: Wallet address to check
            
        Returns:
            Dict with balance information
        """
        url = f"{self.base_url}/contract/{self.chain_id}/{settings.pr_token_contract_address}/erc20/balance-of"
        
        params = {
            "walletAddress": wallet_address
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    result = data.get("result", {})
                    
                    return {
                        "success": True,
                        "balance": result.get("value", "0"),
                        "display_value": result.get("displayValue", "0"),
                        "symbol": result.get("symbol", "PR"),
                        "data": data
                    }
                else:
                    error_msg = f"Thirdweb balance API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "error": error_msg
                    }
                    
        except Exception as e:
            error_msg = f"Error getting token balance for {wallet_address}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    async def wait_for_transaction(
        self, 
        queue_id: str, 
        max_wait_seconds: int = 300
    ) -> Dict[str, any]:
        """
        Wait for a transaction to be mined.
        
        Args:
            queue_id: Queue ID from Thirdweb transaction
            max_wait_seconds: Maximum time to wait
            
        Returns:
            Dict with final transaction status
        """
        import asyncio
        
        wait_time = 0
        check_interval = 5  # Check every 5 seconds
        
        while wait_time < max_wait_seconds:
            status_result = await self.get_transaction_status(queue_id)
            
            if not status_result["success"]:
                return status_result
            
            status = status_result.get("status")
            
            if status == "mined":
                return {
                    "success": True,
                    "status": "completed",
                    "transaction_hash": status_result.get("transaction_hash")
                }
            elif status == "errored":
                return {
                    "success": False,
                    "error": status_result.get("error_message", "Transaction failed"),
                    "status": "failed"
                }
            
            # Still pending, wait and check again
            await asyncio.sleep(check_interval)
            wait_time += check_interval
        
        return {
            "success": False,
            "error": f"Transaction timed out after {max_wait_seconds} seconds",
            "status": "timeout"
        }

    async def estimate_gas(self, to_address: str, amount: int) -> Dict[str, any]:
        """
        Estimate gas cost for token transfer.
        
        Args:
            to_address: Recipient address
            amount: Amount to transfer
            
        Returns:
            Dict with gas estimation
        """
        # For ERC-20 transfers, gas is usually around 21000-65000
        # This is a simplified estimation
        estimated_gas = 65000
        
        return {
            "success": True,
            "estimated_gas": estimated_gas,
            "estimated_gas_price": "20000000000",  # 20 gwei in wei
            "estimated_cost_wei": str(estimated_gas * 20000000000)
        }


# Global instance
thirdweb_service = ThirdwebService()