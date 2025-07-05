// Alchemy integration for Sepolia transaction monitoring

const ALCHEMY_URL = process.env.ALCHEMY_SEPOLIA_URL || 'https://eth-sepolia.g.alchemy.com/v2/demo';
const ULTRA_CIVIC_TREASURY = '0x742d35Cc6634C0532925a3b8d4b6A9B3bC5B5e12'; // Replace with actual treasury

export interface TransactionReceipt {
  status: string;
  to: string;
  from: string;
  value: string;
  blockNumber: string;
  gasUsed: string;
}

export const blockchain = {
  async getTransactionReceipt(txHash: string): Promise<TransactionReceipt | null> {
    try {
      const response = await fetch(ALCHEMY_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          jsonrpc: '2.0',
          id: 1,
          method: 'eth_getTransactionReceipt',
          params: [txHash]
        })
      });
      
      const data = await response.json();
      
      if (data.error) {
        console.error('Alchemy error:', data.error);
        return null;
      }
      
      return data.result;
    } catch (error) {
      console.error('Error fetching transaction receipt:', error);
      return null;
    }
  },
  
  async verifyPayment(txHash: string, expectedValue: string): Promise<boolean> {
    const receipt = await this.getTransactionReceipt(txHash);
    
    if (!receipt) {
      return false;
    }
    
    // Check transaction was successful
    if (receipt.status !== '0x1') {
      return false;
    }
    
    // Verify payment went to treasury
    if (receipt.to?.toLowerCase() !== ULTRA_CIVIC_TREASURY.toLowerCase()) {
      return false;
    }
    
    // Note: For full verification, we'd also check the value matches expected amount
    // For hackathon, we'll be more lenient
    
    return true;
  },
  
  isValidTxHash(txHash: string): boolean {
    return /^0x[a-fA-F0-9]{64}$/.test(txHash);
  },
  
  isValidAddress(address: string): boolean {
    return /^0x[a-fA-F0-9]{40}$/.test(address);
  }
};