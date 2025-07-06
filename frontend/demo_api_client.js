// Demo API client for hackathon - bypasses backend issues
// Replace your existing API calls with these for quick demo

const DEMO_API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Demo API client
export class DemoApiClient {
  static async reserveAllowances(numAllowances, wallet, message) {
    try {
      const response = await fetch(`${DEMO_API_BASE}/demo/retirements`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          num_allowances: numAllowances,
          wallet: wallet,
          message: message || ''
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to reserve allowances');
      }

      return await response.json();
    } catch (error) {
      console.error('Demo reservation error:', error);
      throw error;
    }
  }

  static async confirmPayment(orderId, txHash) {
    try {
      const response = await fetch(`${DEMO_API_BASE}/demo/retirements/confirm`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          order_id: orderId,
          tx_hash: txHash
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to confirm payment');
      }

      return await response.json();
    } catch (error) {
      console.error('Demo payment confirmation error:', error);
      throw error;
    }
  }

  static async getOrderStatus(orderId) {
    try {
      const response = await fetch(`${DEMO_API_BASE}/demo/retirements/status/${orderId}`);
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get order status');
      }

      return await response.json();
    } catch (error) {
      console.error('Demo status check error:', error);
      throw error;
    }
  }

  static async getHistory() {
    try {
      const response = await fetch(`${DEMO_API_BASE}/demo/retirements/history`);
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get history');
      }

      return await response.json();
    } catch (error) {
      console.error('Demo history error:', error);
      throw error;
    }
  }

  // Mock wallet connection for demo
  static async mockWalletConnection() {
    // Return a demo wallet address
    return {
      address: '0x742d35Cc6634C0532925a3b8D6aC44dC5A25489e',
      chainId: 11155111, // Sepolia
      connected: true
    };
  }

  // Mock transaction sending for demo
  static async mockSendTransaction(amount) {
    // Simulate transaction delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Return mock transaction hash
    return {
      hash: '0x' + Math.random().toString(16).substring(2, 66).padStart(64, '0'),
      success: true
    };
  }
}

// Demo React hook for easy integration
export function useDemoRetirement() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [orderId, setOrderId] = useState(null);
  const [status, setStatus] = useState('idle');

  const startRetirement = async (numAllowances, message) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Step 1: Mock wallet connection
      const wallet = await DemoApiClient.mockWalletConnection();
      
      // Step 2: Reserve allowances
      const reservation = await DemoApiClient.reserveAllowances(
        numAllowances, 
        wallet.address, 
        message
      );
      
      setOrderId(reservation.order_id);
      setStatus('reserved');
      
      // Step 3: Mock payment
      const tx = await DemoApiClient.mockSendTransaction(numAllowances * 24);
      
      // Step 4: Confirm payment
      const confirmation = await DemoApiClient.confirmPayment(
        reservation.order_id,
        tx.hash
      );
      
      setStatus('completed');
      
      return {
        success: true,
        orderId: reservation.order_id,
        txHash: tx.hash
      };
      
    } catch (err) {
      setError(err.message);
      setStatus('error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    startRetirement,
    isLoading,
    error,
    orderId,
    status
  };
}

// Usage instructions:
/*
1. Replace your existing API calls with DemoApiClient methods
2. Use the useDemoRetirement hook in your React components
3. The demo automatically handles the full flow without external dependencies

Example usage:
```javascript
import { useDemoRetirement } from './demo_api_client';

function RetirementForm() {
  const { startRetirement, isLoading, error, status } = useDemoRetirement();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    const numAllowances = 3;
    const message = "Demo retirement!";
    
    try {
      const result = await startRetirement(numAllowances, message);
      console.log('Retirement completed:', result);
    } catch (err) {
      console.error('Retirement failed:', err);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Processing...' : 'Retire Allowances'}
      </button>
      {error && <p style={{color: 'red'}}>{error}</p>}
      {status === 'completed' && <p style={{color: 'green'}}>Success!</p>}
    </form>
  );
}
```
*/