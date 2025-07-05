'use client'

import { useState, useEffect } from 'react'

export function useEthPrice() {
  const [ethPriceUSD, setEthPriceUSD] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchEthPrice = async () => {
      try {
        setLoading(true)
        const response = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd')
        const data = await response.json()
        setEthPriceUSD(data.ethereum.usd)
        setError(null)
      } catch (err) {
        setError('Failed to fetch ETH price')
        console.error('Error fetching ETH price:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchEthPrice()
    const interval = setInterval(fetchEthPrice, 30000) // Update every 30 seconds
    
    return () => clearInterval(interval)
  }, [])

  const calculateEthAmount = (allowances: number) => {
    if (!ethPriceUSD) return null
    const usdAmount = allowances * 24
    return usdAmount / ethPriceUSD
  }

  return {
    ethPriceUSD,
    loading,
    error,
    calculateEthAmount
  }
}