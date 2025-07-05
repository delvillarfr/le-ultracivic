'use client'

import { ConnectButton } from '@rainbow-me/rainbowkit'
import { useAccount, useChainId } from 'wagmi'
import { sepolia } from 'wagmi/chains'

interface WalletConnectionProps {
  onConnected: () => void;
}

export default function WalletConnection({ onConnected }: WalletConnectionProps) {
  const { isConnected } = useAccount()
  const chainId = useChainId()
  
  if (isConnected && chainId === sepolia.id) {
    onConnected()
    return null
  }
  
  return (
    <div className="wallet-connection">
      <ConnectButton />
      {isConnected && chainId !== sepolia.id && (
        <p className="wrong-network">Please switch to Sepolia testnet</p>
      )}
    </div>
  )
}