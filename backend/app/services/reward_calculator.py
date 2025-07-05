"""Reward calculation service for $PR token distribution."""

import logging
from typing import Dict

from app.config import settings

logger = logging.getLogger(__name__)


class RewardCalculator:
    """Service for calculating $PR token rewards."""

    def __init__(self):
        self.token_decimals = 18  # Standard ERC-20 decimals
        self.base_reward_per_allowance = 1  # 1 $PR token per allowance

    def calculate_reward_amount(self, num_allowances: int) -> Dict[str, any]:
        """
        Calculate reward amount for given number of allowances.
        
        Args:
            num_allowances: Number of allowances retired
            
        Returns:
            Dict with reward calculation
        """
        try:
            if num_allowances <= 0:
                return {
                    "success": False,
                    "error": "Number of allowances must be positive"
                }
            
            # Basic calculation: 1 token per allowance
            base_tokens = num_allowances * self.base_reward_per_allowance
            
            # Apply any bonus multipliers (future feature)
            bonus_multiplier = self._calculate_bonus_multiplier(num_allowances)
            final_tokens = base_tokens * bonus_multiplier
            
            # Convert to token units (with decimals)
            token_amount_units = int(final_tokens * (10 ** self.token_decimals))
            
            return {
                "success": True,
                "reward_calculation": {
                    "num_allowances": num_allowances,
                    "base_reward_per_allowance": self.base_reward_per_allowance,
                    "base_tokens": base_tokens,
                    "bonus_multiplier": bonus_multiplier,
                    "final_tokens": final_tokens,
                    "token_amount_units": token_amount_units,
                    "token_decimals": self.token_decimals,
                    "formatted_amount": f"{final_tokens:.6f} $PR"
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating reward amount: {str(e)}")
            return {
                "success": False,
                "error": f"Reward calculation error: {str(e)}"
            }

    def _calculate_bonus_multiplier(self, num_allowances: int) -> float:
        """
        Calculate bonus multiplier based on number of allowances.
        
        Args:
            num_allowances: Number of allowances
            
        Returns:
            Bonus multiplier (1.0 = no bonus)
        """
        # For now, no bonus system - just return 1.0
        # Future enhancements could include:
        # - Volume bonuses for large purchases
        # - Early adopter bonuses
        # - Seasonal multipliers
        
        if num_allowances >= 50:
            return 1.1  # 10% bonus for large purchases (50+ allowances)
        elif num_allowances >= 20:
            return 1.05  # 5% bonus for medium purchases (20+ allowances)
        else:
            return 1.0  # No bonus for small purchases

    def validate_reward_amount(self, calculated_amount: int, num_allowances: int) -> Dict[str, any]:
        """
        Validate if calculated reward amount is correct.
        
        Args:
            calculated_amount: Calculated token amount in units
            num_allowances: Number of allowances
            
        Returns:
            Dict with validation result
        """
        try:
            # Recalculate expected amount
            expected_calculation = self.calculate_reward_amount(num_allowances)
            
            if not expected_calculation["success"]:
                return expected_calculation
            
            expected_amount = expected_calculation["reward_calculation"]["token_amount_units"]
            
            if calculated_amount != expected_amount:
                return {
                    "success": False,
                    "valid": False,
                    "error": "Reward amount mismatch",
                    "details": {
                        "calculated_amount": calculated_amount,
                        "expected_amount": expected_amount,
                        "difference": abs(calculated_amount - expected_amount),
                        "num_allowances": num_allowances
                    }
                }
            
            return {
                "success": True,
                "valid": True,
                "message": "Reward amount is valid",
                "details": {
                    "token_amount_units": calculated_amount,
                    "token_amount_decimal": calculated_amount / (10 ** self.token_decimals),
                    "num_allowances": num_allowances
                }
            }
            
        except Exception as e:
            logger.error(f"Error validating reward amount: {str(e)}")
            return {
                "success": False,
                "error": f"Reward validation error: {str(e)}"
            }

    def calculate_gas_estimate(self, num_allowances: int) -> Dict[str, any]:
        """
        Estimate gas costs for token transfer.
        
        Args:
            num_allowances: Number of allowances (affects token amount)
            
        Returns:
            Dict with gas estimation
        """
        try:
            # Base gas for ERC-20 transfer: ~21,000 - 65,000 gas
            base_gas = 65000
            
            # Additional gas for larger amounts (minimal impact)
            additional_gas = min(num_allowances * 100, 5000)
            
            total_gas = base_gas + additional_gas
            
            # Estimate gas price (20 gwei for Sepolia)
            gas_price_gwei = 20
            gas_price_wei = gas_price_gwei * 10**9
            
            # Calculate total cost
            total_cost_wei = total_gas * gas_price_wei
            total_cost_eth = total_cost_wei / 10**18
            
            return {
                "success": True,
                "gas_estimate": {
                    "estimated_gas": total_gas,
                    "base_gas": base_gas,
                    "additional_gas": additional_gas,
                    "gas_price_gwei": gas_price_gwei,
                    "gas_price_wei": gas_price_wei,
                    "total_cost_wei": total_cost_wei,
                    "total_cost_eth": total_cost_eth,
                    "formatted_cost": f"{total_cost_eth:.6f} ETH"
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating gas estimate: {str(e)}")
            return {
                "success": False,
                "error": f"Gas estimation error: {str(e)}"
            }

    def get_reward_summary(self, num_allowances: int) -> Dict[str, any]:
        """
        Get complete reward summary for display.
        
        Args:
            num_allowances: Number of allowances
            
        Returns:
            Dict with complete reward information
        """
        try:
            # Calculate reward
            reward_calc = self.calculate_reward_amount(num_allowances)
            if not reward_calc["success"]:
                return reward_calc
            
            # Calculate gas estimate
            gas_estimate = self.calculate_gas_estimate(num_allowances)
            if not gas_estimate["success"]:
                return gas_estimate
            
            reward_details = reward_calc["reward_calculation"]
            gas_details = gas_estimate["gas_estimate"]
            
            return {
                "success": True,
                "reward_summary": {
                    "allowances_retired": num_allowances,
                    "tokens_earned": reward_details["final_tokens"],
                    "tokens_formatted": reward_details["formatted_amount"],
                    "bonus_applied": reward_details["bonus_multiplier"] > 1.0,
                    "bonus_multiplier": reward_details["bonus_multiplier"],
                    "token_amount_units": reward_details["token_amount_units"],
                    "estimated_gas_cost": gas_details["formatted_cost"],
                    "estimated_gas": gas_details["estimated_gas"],
                    "environmental_impact": {
                        "co2_reduced_tons": num_allowances,  # 1 allowance = 1 ton CO2
                        "impact_description": f"You'll prevent {num_allowances} tons of CO₂ from being emitted!"
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting reward summary: {str(e)}")
            return {
                "success": False,
                "error": f"Reward summary error: {str(e)}"
            }


# Global instance
reward_calculator = RewardCalculator()