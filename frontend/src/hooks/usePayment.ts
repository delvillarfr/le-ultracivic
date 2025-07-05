'use client'

import { useSendTransaction, useWaitForTransactionReceipt } from 'wagmi'
import { parseEther } from 'viem'
import { useEthPrice } from './useEthPrice'

const ULTRA_CIVIC_TREASURY = '0x742d35Cc6634C0532925a3b8d4b6A9B3bC5B5e12' // Replace with actual treasury address

export function usePayment() {
  const { calculateEthAmount } = useEthPrice()
  const { sendTransaction, data: hash, isPending: isTransactionPending, error: transactionError } = useSendTransaction()
  const { isLoading: isConfirming, isSuccess: isConfirmed } = useWaitForTransactionReceipt({
    hash,
  })

  const initiatePayment = async (allowances: number) => {
    const ethAmount = calculateEthAmount(allowances)
    if (!ethAmount) {
      throw new Error('Unable to calculate ETH amount')
    }

    try {
      sendTransaction({
        to: ULTRA_CIVIC_TREASURY,
        value: parseEther(ethAmount.toString()),
      })
    } catch (error) {
      console.error('Payment failed:', error)
      throw error
    }
  }

  return {
    initiatePayment,
    hash,
    isTransactionPending,
    isConfirming,
    isConfirmed,
    transactionError,
    calculateEthAmount
  }
}