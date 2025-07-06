'use client'

import { useState, useEffect } from 'react'
import { api, HistoryResponse } from '@/lib/api'

export function useHistory() {
  const [history, setHistory] = useState<HistoryResponse['retirements']>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const addDemoEntry = (message: string, wallet: string) => {
    // Generate mock serial numbers
    const numAllowances = Math.floor(Math.random() * 5) + 1 // 1-5 allowances
    const mockSerialNumbers = Array.from({ length: numAllowances }, (_, i) => 
      `PR-${Math.random().toString(36).substring(2, 8).toUpperCase()}-${(i + 1).toString().padStart(3, '0')}`
    ).join(', ')
    
    // Generate mock transaction hash
    const mockTxHash = `0x${Math.random().toString(16).substring(2, 42).padEnd(40, '0')}`
    
    const demoEntry = {
      serial_number: mockSerialNumbers,
      message: message || "they will say, 'This land that was laid waste has become like the garden of Eden' Ezequiel 36:35",
      wallet: wallet,
      timestamp: new Date().toISOString(),
      tx_hash: mockTxHash,
      reward_tx_hash: mockTxHash
    }
    
    setHistory(prev => [demoEntry, ...prev])
  }

  const fetchHistory = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await api.getHistory()
      setHistory(response.retirements)
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to fetch history')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchHistory()
  }, [])

  const refreshHistory = () => {
    fetchHistory()
  }

  return {
    history,
    isLoading,
    error,
    refreshHistory,
    addDemoEntry
  }
}