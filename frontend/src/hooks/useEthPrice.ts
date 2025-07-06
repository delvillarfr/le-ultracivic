'use client'

import { useState, useEffect } from 'react'
import CONFIG from '@/lib/config'

export function useEthPrice() {
  // Mock price for demo - avoid external API calls
  const [ethPriceUSD, setEthPriceUSD] = useState<number | null>(2500)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // No external API calls for demo
    setEthPriceUSD(2500) // Fixed demo price
    setLoading(false)
    setError(null)
  }, [])

  const calculateEthAmount = (allowances: number) => {
    if (!ethPriceUSD) return null
    const usdAmount = allowances * CONFIG.PRICE_PER_ALLOWANCE_USD
    return usdAmount / ethPriceUSD
  }

  return {
    ethPriceUSD,
    loading,
    error,
    calculateEthAmount
  }
}