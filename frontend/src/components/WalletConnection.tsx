'use client'

import { ConnectButton } from '@rainbow-me/rainbowkit'
import { useAccount, useChainId } from 'wagmi'
import { sepolia } from 'wagmi/chains'
import LoadingSpinner from './ui/LoadingSpinner'

interface WalletConnectionProps {
  onConnected: () => void;
  isConnecting?: boolean;
}

export default function WalletConnection({ onConnected, isConnecting = false }: WalletConnectionProps) {
  const { isConnected } = useAccount()
  const chainId = useChainId()
  
  if (isConnected && chainId === sepolia.id) {
    onConnected()
    return null
  }
  
  return (
    <div className="wallet-connection fade-in">
      {isConnecting ? (
        <div className="connecting-state">
          <LoadingSpinner size="medium" />
          <p>Connecting wallet...</p>
        </div>
      ) : (
        <>
          <ConnectButton />
          {isConnected && chainId !== sepolia.id && (
            <div className="network-warning slide-in">
              <LoadingSpinner size="small" />
              <p className="wrong-network">Switching to Sepolia testnet...</p>
            </div>
          )}
        </>
      )}
    </div>
  )
}