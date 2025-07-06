// Configuration constants for the application

export const CONFIG = {
  // Default values for the allowance form
  DEFAULT_ALLOWANCES: parseInt(process.env.NEXT_PUBLIC_DEFAULT_ALLOWANCES || '1'),
  
  // Pricing configuration
  PRICE_PER_ALLOWANCE_USD: parseInt(process.env.NEXT_PUBLIC_PRICE_PER_ALLOWANCE || '24'),
  
  // Environmental impact calculation
  CO2_TONS_PER_ALLOWANCE: parseInt(process.env.NEXT_PUBLIC_CO2_TONS_PER_ALLOWANCE || '1'),
  
  // Form validation limits
  MIN_ALLOWANCES: 1,
  MAX_ALLOWANCES: 99,
  MAX_MESSAGE_LENGTH: 100,
  
  // Treasury configuration
  TREASURY_ADDRESS: process.env.NEXT_PUBLIC_TREASURY_ADDRESS || '0x742d35cc6634c0532925a3b8d11d2d7d2ae30b2b',
  
  // Token reward ratio (1:1 by default)
  TOKENS_PER_ALLOWANCE: parseInt(process.env.NEXT_PUBLIC_TOKENS_PER_ALLOWANCE || '1'),
  
  // Social impact multiplier
  SOCIAL_IMPACT_MULTIPLIER: 230,
} as const

export default CONFIG