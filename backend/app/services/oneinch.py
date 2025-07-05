"""1inch service for price quotes and swap information."""

import logging
from typing import Dict, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class OneInchService:
    """Service for interacting with 1inch API for price quotes."""

    def __init__(self):
        self.base_url = settings.oneinch_api_url  # https://api.1inch.io/v5.0/11155111
        self.timeout = httpx.Timeout(30.0)
        
        # Common token addresses on Sepolia
        self.token_addresses = {
            "ETH": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",  # Native ETH
            "USDC": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",  # USDC on Sepolia
            "USDT": "0x7169D38820dfd117C3FA1f22a697dBA58d90BA06",  # USDT on Sepolia
        }

    async def get_quote(
        self,
        from_token: str,
        to_token: str,
        amount: str
    ) -> Dict[str, any]:
        """
        Get price quote from 1inch API.
        
        Args:
            from_token: Source token symbol or address
            to_token: Destination token symbol or address  
            amount: Amount in smallest token unit (wei for ETH)
            
        Returns:
            Dict with quote information
        """
        # Convert token symbols to addresses
        from_token_addr = self._get_token_address(from_token)
        to_token_addr = self._get_token_address(to_token)
        
        if not from_token_addr or not to_token_addr:
            return {
                "success": False,
                "error": f"Unsupported token: {from_token} or {to_token}"
            }
        
        url = f"{self.base_url}/quote"
        params = {
            "fromTokenAddress": from_token_addr,
            "toTokenAddress": to_token_addr,
            "amount": amount
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    return {
                        "success": True,
                        "from_token": data.get("fromToken", {}),
                        "to_token": data.get("toToken", {}),
                        "from_amount": data.get("fromTokenAmount"),
                        "to_amount": data.get("toTokenAmount"),
                        "estimated_gas": data.get("estimatedGas"),
                        "data": data
                    }
                else:
                    error_msg = f"1inch API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "error": error_msg,
                        "status_code": response.status_code
                    }
                    
        except httpx.TimeoutException:
            error_msg = "Timeout getting quote from 1inch"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Error getting quote from 1inch: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    async def get_eth_price_in_usd(self) -> Dict[str, any]:
        """
        Get current ETH price in USD using external price API.
        
        Returns:
            Dict with ETH price information
        """
        # Using CoinGecko API as fallback for ETH price
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "ethereum",
            "vs_currencies": "usd"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    eth_price = data.get("ethereum", {}).get("usd")
                    
                    if eth_price:
                        return {
                            "success": True,
                            "price_usd": eth_price,
                            "source": "coingecko"
                        }
                    else:
                        return {
                            "success": False,
                            "error": "ETH price not found in response"
                        }
                else:
                    error_msg = f"Price API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "error": error_msg
                    }
                    
        except Exception as e:
            error_msg = f"Error getting ETH price: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    async def calculate_eth_amount_for_usd(self, usd_amount: float) -> Dict[str, any]:
        """
        Calculate how much ETH is needed for a given USD amount.
        
        Args:
            usd_amount: Amount in USD
            
        Returns:
            Dict with ETH amount calculation
        """
        price_result = await self.get_eth_price_in_usd()
        
        if not price_result["success"]:
            return price_result
        
        eth_price = price_result["price_usd"]
        eth_amount = usd_amount / eth_price
        eth_amount_wei = int(eth_amount * 10**18)  # Convert to wei
        
        return {
            "success": True,
            "usd_amount": usd_amount,
            "eth_price_usd": eth_price,
            "eth_amount": eth_amount,
            "eth_amount_wei": eth_amount_wei,
            "eth_amount_formatted": f"{eth_amount:.6f} ETH"
        }

    async def get_swap_data(
        self,
        from_token: str,
        to_token: str,
        amount: str,
        from_address: str,
        slippage: float = 1.0
    ) -> Dict[str, any]:
        """
        Get swap transaction data from 1inch.
        
        Args:
            from_token: Source token symbol or address
            to_token: Destination token symbol or address
            amount: Amount to swap
            from_address: Address executing the swap
            slippage: Slippage tolerance (1.0 = 1%)
            
        Returns:
            Dict with swap transaction data
        """
        from_token_addr = self._get_token_address(from_token)
        to_token_addr = self._get_token_address(to_token)
        
        if not from_token_addr or not to_token_addr:
            return {
                "success": False,
                "error": f"Unsupported token: {from_token} or {to_token}"
            }
        
        url = f"{self.base_url}/swap"
        params = {
            "fromTokenAddress": from_token_addr,
            "toTokenAddress": to_token_addr,
            "amount": amount,
            "fromAddress": from_address,
            "slippage": slippage
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    transaction = data.get("tx", {})
                    
                    return {
                        "success": True,
                        "transaction": transaction,
                        "to_token_amount": data.get("toTokenAmount"),
                        "data": data
                    }
                else:
                    error_msg = f"1inch swap API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "error": error_msg
                    }
                    
        except Exception as e:
            error_msg = f"Error getting swap data: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    def _get_token_address(self, token: str) -> Optional[str]:
        """
        Get token address from symbol or return address if already provided.
        
        Args:
            token: Token symbol or address
            
        Returns:
            Token address or None if not found
        """
        # If it's already an address (starts with 0x and is 42 chars)
        if token.startswith("0x") and len(token) == 42:
            return token
        
        # Look up symbol in known addresses
        return self.token_addresses.get(token.upper())

    async def get_supported_tokens(self) -> Dict[str, any]:
        """
        Get list of supported tokens from 1inch.
        
        Returns:
            Dict with supported tokens
        """
        url = f"{self.base_url}/tokens"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "tokens": data.get("tokens", {}),
                        "count": len(data.get("tokens", {}))
                    }
                else:
                    error_msg = f"1inch tokens API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "error": error_msg
                    }
                    
        except Exception as e:
            error_msg = f"Error getting supported tokens: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }


# Global instance
oneinch_service = OneInchService()