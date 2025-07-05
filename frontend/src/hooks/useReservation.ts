'use client'

import { useState } from 'react'
import { api, ReserveRequest, ReserveResponse } from '@/lib/api'

export function useReservation() {
  const [isReserving, setIsReserving] = useState(false)
  const [reservationError, setReservationError] = useState<string | null>(null)
  const [reservation, setReservation] = useState<ReserveResponse | null>(null)

  const reserveAllowances = async (request: ReserveRequest): Promise<ReserveResponse | null> => {
    setIsReserving(true)
    setReservationError(null)
    
    try {
      const response = await api.reserveAllowances(request)
      setReservation(response)
      return response
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to reserve allowances'
      setReservationError(errorMessage)
      return null
    } finally {
      setIsReserving(false)
    }
  }

  const clearReservation = () => {
    setReservation(null)
    setReservationError(null)
  }

  return {
    isReserving,
    reservationError,
    reservation,
    reserveAllowances,
    clearReservation
  }
}