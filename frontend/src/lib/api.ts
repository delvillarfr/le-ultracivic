// API service layer for backend calls

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:3000/api';

export interface ReserveRequest {
  num_allowances: number;
  message: string;
  wallet: string;
}

export interface ReserveResponse {
  order_id: string;
  serial_numbers: string[];
}

export interface ConfirmRequest {
  txHash: string;
  order_id: string;
}

export interface ConfirmResponse {
  status: string;
}

export interface StatusResponse {
  status: 'pending' | 'paid_but_not_retired' | 'completed' | 'error';
  tx_hash?: string;
  serial_numbers?: string[];
  reward_tx_hash?: string;
}

export interface HistoryResponse {
  retirements: Array<{
    serial_number: string;
    message: string;
    wallet: string;
    timestamp: string;
    tx_hash?: string;
    reward_tx_hash?: string;
  }>;
  total: number;
}

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function apiCall<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new ApiError(response.status, errorData.error || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    
    // Network or other errors
    throw new ApiError(0, error instanceof Error ? error.message : 'Network error');
  }
}

export const api = {
  async reserveAllowances(request: ReserveRequest): Promise<ReserveResponse> {
    return apiCall<ReserveResponse>('/retirements', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  async confirmPayment(request: ConfirmRequest): Promise<ConfirmResponse> {
    return apiCall<ConfirmResponse>('/retirements/confirm', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  async getOrderStatus(order_id: string): Promise<StatusResponse> {
    return apiCall<StatusResponse>(`/retirements/status/${order_id}`);
  },

  async getHistory(): Promise<HistoryResponse> {
    return apiCall<HistoryResponse>('/retirements/history');
  },
};

// Polling utility with exponential backoff
export async function pollOrderStatus(
  order_id: string,
  onUpdate: (status: StatusResponse) => void,
  onComplete: (status: StatusResponse) => void,
  onError: (error: Error) => void
): Promise<void> {
  let attempt = 0;
  const maxAttempts = 150; // 5 minutes at 2-second intervals
  
  const poll = async () => {
    try {
      const status = await api.getOrderStatus(order_id);
      onUpdate(status);
      
      if (status.status === 'completed' || status.status === 'error') {
        onComplete(status);
        return;
      }
      
      attempt++;
      if (attempt >= maxAttempts) {
        onError(new Error('Polling timeout'));
        return;
      }
      
      // 2-second intervals with exponential backoff on errors
      const delay = 2000;
      setTimeout(poll, delay);
      
    } catch (error) {
      attempt++;
      if (attempt >= maxAttempts) {
        onError(error instanceof Error ? error : new Error('Polling failed'));
        return;
      }
      
      // Exponential backoff on errors (up to 30 seconds)
      const delay = Math.min(2000 * Math.pow(2, Math.floor(attempt / 5)), 30000);
      setTimeout(poll, delay);
    }
  };
  
  poll();
}