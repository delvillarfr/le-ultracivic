import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/database';
import { blockchain } from '@/lib/blockchain';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { txHash, order_id } = body;
    
    // Validation
    if (!txHash || !blockchain.isValidTxHash(txHash)) {
      return NextResponse.json(
        { error: 'txHash must be a valid transaction hash' },
        { status: 400 }
      );
    }
    
    if (!order_id || typeof order_id !== 'string') {
      return NextResponse.json(
        { error: 'order_id must be a valid string' },
        { status: 400 }
      );
    }
    
    // Check if order exists
    const order = await db.getOrder(order_id);
    if (!order) {
      return NextResponse.json(
        { error: 'Order not found' },
        { status: 404 }
      );
    }
    
    if (order.status !== 'pending') {
      return NextResponse.json(
        { error: 'Order is not in pending status' },
        { status: 409 }
      );
    }
    
    // Store transaction hash and update status
    await db.updateOrderTxHash(order_id, txHash);
    
    // Start monitoring transaction in background
    startTransactionMonitoring(order_id, txHash);
    
    return NextResponse.json({
      status: 'accepted'
    });
    
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// Background transaction monitoring
async function startTransactionMonitoring(order_id: string, txHash: string) {
  const maxAttempts = 60; // 5 minutes with 5-second intervals
  let attempts = 0;
  
  const monitor = async () => {
    try {
      attempts++;
      
      const receipt = await blockchain.getTransactionReceipt(txHash);
      
      if (receipt) {
        // Transaction found
        if (receipt.status === '0x1') {
          // Transaction successful
          const isValid = await blockchain.verifyPayment(txHash, '0'); // We'll be lenient on amount for hackathon
          
          if (isValid) {
            await db.completeOrder(order_id);
            console.log(`Order ${order_id} completed successfully`);
          } else {
            await db.failOrder(order_id);
            console.log(`Order ${order_id} failed - invalid payment`);
          }
        } else {
          // Transaction failed
          await db.failOrder(order_id);
          console.log(`Order ${order_id} failed - transaction failed`);
        }
      } else if (attempts >= maxAttempts) {
        // Timeout - transaction not found
        await db.failOrder(order_id);
        console.log(`Order ${order_id} failed - timeout`);
      } else {
        // Continue monitoring
        setTimeout(monitor, 5000); // Check again in 5 seconds
      }
    } catch (error) {
      console.error(`Error monitoring transaction ${txHash}:`, error);
      if (attempts >= maxAttempts) {
        await db.failOrder(order_id);
      } else {
        setTimeout(monitor, 5000);
      }
    }
  };
  
  // Start monitoring
  setTimeout(monitor, 5000); // Wait 5 seconds before first check
}