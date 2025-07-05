"""Real-time pricing service for payment calculations."""

import logging
from typing import Dict, Optional

from app.config import settings
from app.services.oneinch import oneinch_service

logger = logging.getLogger(__name__)


class PriceService:
    """Service for real-time price calculations and payment validation."""

    def __init__(self):
        self.allowance_price_usd = settings.allowance_price_usd
        self.slippage_tolerance = settings.price_slippage_tolerance

    async def get_current_eth_price_usd(self) -> Dict[str, any]:
        """
        Get current ETH price in USD.
        
        Returns:
            Dict with price information
        """
        try:
            # Try 1inch first, fallback to CoinGecko
            price_result = await oneinch_service.get_eth_price_in_usd()
            
            if price_result["success"]:
                return {
                    "success": True,
                    "price_usd": price_result["price_usd"],
                    "source": "coingecko",
                    "timestamp": "now"
                }
            else:
                # Fallback to a reasonable default if both APIs fail
                logger.warning(f"Price API failed: {price_result.get('error')}, using fallback price")
                return {
                    "success": True,
                    "price_usd": 2500.0,  # Fallback ETH price
                    "source": "fallback",
                    "timestamp": "now",
                    "warning": "Using fallback price due to API failure"
                }
                
        except Exception as e:
            logger.error(f"Error getting ETH price: {str(e)}")
            return {
                "success": False,
                "error": f"Price lookup error: {str(e)}"
            }

    async def calculate_payment_amount(self, num_allowances: int) -> Dict[str, any]:
        """
        Calculate required payment amount in ETH for given number of allowances.
        
        Args:
            num_allowances: Number of allowances to purchase
            
        Returns:
            Dict with payment calculation
        """
        try:
            # Get current ETH price
            price_result = await self.get_current_eth_price_usd()
            
            if not price_result["success"]:
                return price_result
            
            eth_price_usd = price_result["price_usd"]
            
            # Calculate total USD amount
            total_usd = num_allowances * self.allowance_price_usd
            
            # Calculate ETH amount needed
            eth_amount = total_usd / eth_price_usd
            eth_amount_wei = int(eth_amount * 10**18)
            
            # Calculate with slippage tolerance
            min_eth_amount = eth_amount * (1 - self.slippage_tolerance)
            max_eth_amount = eth_amount * (1 + self.slippage_tolerance)
            
            min_eth_wei = int(min_eth_amount * 10**18)
            max_eth_wei = int(max_eth_amount * 10**18)
            
            return {
                "success": True,
                "payment_calculation": {
                    "num_allowances": num_allowances,
                    "allowance_price_usd": self.allowance_price_usd,
                    "total_usd": total_usd,
                    "eth_price_usd": eth_price_usd,
                    "eth_amount": eth_amount,
                    "eth_amount_wei": eth_amount_wei,
                    "eth_amount_formatted": f"{eth_amount:.6f} ETH",
                    "slippage_tolerance": self.slippage_tolerance,
                    "min_eth_amount": min_eth_amount,
                    "max_eth_amount": max_eth_amount,
                    "min_eth_wei": min_eth_wei,
                    "max_eth_wei": max_eth_wei,
                    "price_source": price_result.get("source", "unknown")
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating payment amount: {str(e)}")
            return {
                "success": False,
                "error": f"Payment calculation error: {str(e)}"
            }

    async def validate_payment_amount(
        self, 
        num_allowances: int, 
        payment_amount_wei: int
    ) -> Dict[str, any]:
        """
        Validate if payment amount is sufficient for the number of allowances.
        
        Args:
            num_allowances: Number of allowances requested
            payment_amount_wei: Payment amount in wei
            
        Returns:
            Dict with validation result
        """
        try:
            # Calculate expected payment
            calculation = await self.calculate_payment_amount(num_allowances)
            
            if not calculation["success"]:
                return calculation
            
            payment_calc = calculation["payment_calculation"]
            min_required_wei = payment_calc["min_eth_wei"]
            max_accepted_wei = payment_calc["max_eth_wei"]
            expected_wei = payment_calc["eth_amount_wei"]
            
            # Validate payment amount
            if payment_amount_wei < min_required_wei:
                return {
                    "success": False,
                    "valid": False,
                    "error": "Insufficient payment amount",
                    "details": {
                        "payment_amount_wei": payment_amount_wei,
                        "payment_amount_eth": payment_amount_wei / 10**18,
                        "required_min_wei": min_required_wei,
                        "required_min_eth": min_required_wei / 10**18,
                        "shortfall_wei": min_required_wei - payment_amount_wei,
                        "shortfall_eth": (min_required_wei - payment_amount_wei) / 10**18
                    }
                }
            
            if payment_amount_wei > max_accepted_wei:
                return {
                    "success": False,
                    "valid": False,
                    "error": "Payment amount exceeds maximum accepted (outside slippage tolerance)",
                    "details": {
                        "payment_amount_wei": payment_amount_wei,
                        "payment_amount_eth": payment_amount_wei / 10**18,
                        "max_accepted_wei": max_accepted_wei,
                        "max_accepted_eth": max_accepted_wei / 10**18,
                        "excess_wei": payment_amount_wei - max_accepted_wei,
                        "excess_eth": (payment_amount_wei - max_accepted_wei) / 10**18
                    }
                }
            
            return {
                "success": True,
                "valid": True,
                "message": "Payment amount is valid",
                "details": {
                    "payment_amount_wei": payment_amount_wei,
                    "payment_amount_eth": payment_amount_wei / 10**18,
                    "expected_wei": expected_wei,
                    "expected_eth": expected_wei / 10**18,
                    "within_tolerance": True,
                    "slippage_used": abs(payment_amount_wei - expected_wei) / expected_wei
                },
                "price_info": payment_calc
            }
            
        except Exception as e:
            logger.error(f"Error validating payment amount: {str(e)}")
            return {
                "success": False,
                "error": f"Payment validation error: {str(e)}"
            }

    async def get_payment_estimate(self, num_allowances: int) -> Dict[str, any]:
        """
        Get payment estimate for frontend display.
        
        Args:
            num_allowances: Number of allowances
            
        Returns:
            Dict with payment estimate
        """
        try:
            calculation = await self.calculate_payment_amount(num_allowances)
            
            if not calculation["success"]:
                return calculation
            
            payment_calc = calculation["payment_calculation"]
            
            return {
                "success": True,
                "estimate": {
                    "num_allowances": num_allowances,
                    "total_usd": payment_calc["total_usd"],
                    "eth_amount": payment_calc["eth_amount"],
                    "eth_amount_formatted": payment_calc["eth_amount_formatted"],
                    "eth_price_usd": payment_calc["eth_price_usd"],
                    "slippage_tolerance": f"{self.slippage_tolerance * 100:.1f}%",
                    "min_eth_amount": payment_calc["min_eth_amount"],
                    "max_eth_amount": payment_calc["max_eth_amount"],
                    "price_source": payment_calc["price_source"],
                    "display_text": f"~${payment_calc['total_usd']} ({payment_calc['eth_amount_formatted']})"
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting payment estimate: {str(e)}")
            return {
                "success": False,
                "error": f"Estimate error: {str(e)}"
            }


# Global instance
price_service = PriceService()