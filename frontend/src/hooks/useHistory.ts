'use client'

import { useState, useEffect } from 'react'
import { api, HistoryResponse } from '@/lib/api'

export function useHistory() {
  const [history, setHistory] = useState<HistoryResponse['retirements']>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

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
    refreshHistory
  }
}