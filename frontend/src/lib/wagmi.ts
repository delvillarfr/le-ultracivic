import { createConfig, http } from 'wagmi'
import { sepolia } from 'wagmi/chains'
import { getDefaultConfig } from '@rainbow-me/rainbowkit'

export const config = getDefaultConfig({
  appName: 'Ultra Civic',
  projectId: process.env.NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID || 'a74b58601c115168dd2c3a9238d17253',
  chains: [sepolia],
  transports: {
    [sepolia.id]: http(),
  },
})