'use client'

import { useAccount, useChainId } from 'wagmi'
import { sepolia } from 'wagmi/chains'

export function useWalletConnection() {
  const { address, isConnected } = useAccount()
  const chainId = useChainId()
  
  const isCorrectChain = chainId === sepolia.id
  const isReady = isConnected && isCorrectChain
  
  return {
    address,
    isConnected,
    isCorrectChain,
    isReady,
    chainId
  }
}