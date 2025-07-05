// Database connection to PostgreSQL for allowances table

import { Pool } from 'pg';

// Validate environment variables
if (!process.env.DATABASE_URL) {
  throw new Error('DATABASE_URL environment variable is required');
}

// Create connection pool with proper configuration for Neon
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false
  },
  max: 10,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 10000,
});

// Test connection on startup
pool.on('connect', () => {
  console.log('Connected to PostgreSQL database');
});

pool.on('error', (err) => {
  console.error('PostgreSQL pool error:', err);
});

export interface Allowance {
  serial_number: string;
  status: 'available' | 'reserved' | 'retired';
  order_id?: string;
  timestamp?: Date;
  wallet?: string;
  message?: string;
  tx_hash?: string;
  reward_tx_hash?: string;
  created_at?: Date;
  updated_at?: Date;
}

export interface Order {
  order_id: string;
  num_allowances: number;
  wallet: string;
  message: string;
  timestamp: Date;
  tx_hash?: string;
  status: 'pending' | 'paid_but_not_retired' | 'completed' | 'error';
  serial_numbers: string[];
}

export const db = {
  async reserveAllowances(num_allowances: number, wallet: string, message: string, order_id: string): Promise<string[]> {
    const client = await pool.connect();
    
    try {
      await client.query('BEGIN');
      
      // Find and lock available allowances
      const result = await client.query(
        `SELECT serial_number FROM allowances 
         WHERE status = 'available' 
         ORDER BY serial_number 
         LIMIT $1 
         FOR UPDATE SKIP LOCKED`,
        [num_allowances]
      );
      
      if (result.rows.length < num_allowances) {
        throw new Error(`Only ${result.rows.length} allowances available, requested ${num_allowances}`);
      }
      
      const serial_numbers = result.rows.map(row => row.serial_number);
      
      // Update allowances to reserved
      await client.query(
        `UPDATE allowances 
         SET status = 'reserved', 
             order_id = $1, 
             wallet = $2, 
             message = $3, 
             timestamp = NOW(),
             updated_at = NOW()
         WHERE serial_number = ANY($4)`,
        [order_id, wallet, message, serial_numbers]
      );
      
      await client.query('COMMIT');
      return serial_numbers;
      
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  },
  
  async getOrder(order_id: string): Promise<Order | null> {
    const client = await pool.connect();
    
    try {
      const result = await client.query(
        `SELECT 
           order_id,
           wallet,
           message,
           timestamp,
           tx_hash,
           ARRAY_AGG(serial_number) as serial_numbers,
           COUNT(*) as num_allowances,
           CASE 
             WHEN BOOL_AND(status = 'retired') THEN 'completed'
             WHEN BOOL_AND(status = 'reserved') AND tx_hash IS NOT NULL THEN 'paid_but_not_retired'
             WHEN BOOL_AND(status = 'reserved') THEN 'pending'
             ELSE 'error'
           END as status
         FROM allowances 
         WHERE order_id = $1 
         GROUP BY order_id, wallet, message, timestamp, tx_hash`,
        [order_id]
      );
      
      if (result.rows.length === 0) {
        return null;
      }
      
      const row = result.rows[0];
      return {
        order_id: row.order_id,
        num_allowances: parseInt(row.num_allowances),
        wallet: row.wallet,
        message: row.message,
        timestamp: row.timestamp,
        tx_hash: row.tx_hash,
        status: row.status,
        serial_numbers: row.serial_numbers
      };
      
    } finally {
      client.release();
    }
  },
  
  async updateOrderTxHash(order_id: string, tx_hash: string): Promise<void> {
    const client = await pool.connect();
    
    try {
      await client.query(
        `UPDATE allowances 
         SET tx_hash = $1, updated_at = NOW() 
         WHERE order_id = $2`,
        [tx_hash, order_id]
      );
    } finally {
      client.release();
    }
  },
  
  async completeOrder(order_id: string): Promise<void> {
    const client = await pool.connect();
    
    try {
      await client.query(
        `UPDATE allowances 
         SET status = 'retired', updated_at = NOW() 
         WHERE order_id = $1`,
        [order_id]
      );
    } finally {
      client.release();
    }
  },
  
  async failOrder(order_id: string): Promise<void> {
    const client = await pool.connect();
    
    try {
      await client.query(
        `UPDATE allowances 
         SET status = 'available', 
             order_id = NULL, 
             wallet = NULL, 
             message = NULL, 
             timestamp = NULL, 
             tx_hash = NULL,
             updated_at = NOW()
         WHERE order_id = $1`,
        [order_id]
      );
    } finally {
      client.release();
    }
  },
  
  async getRetiredAllowances(): Promise<Allowance[]> {
    const client = await pool.connect();
    
    try {
      const result = await client.query(
        `SELECT * FROM allowances 
         WHERE status = 'retired' 
         ORDER BY timestamp DESC 
         LIMIT 50`
      );
      
      return result.rows;
    } finally {
      client.release();
    }
  }
};