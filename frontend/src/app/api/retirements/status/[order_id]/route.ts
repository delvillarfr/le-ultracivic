import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/database';

export async function GET(
  request: NextRequest,
  { params }: { params: { order_id: string } }
) {
  try {
    const { order_id } = params;
    
    if (!order_id || typeof order_id !== 'string') {
      return NextResponse.json(
        { error: 'order_id must be a valid string' },
        { status: 400 }
      );
    }
    
    // Get order
    const order = await db.getOrder(order_id);
    if (!order) {
      return NextResponse.json(
        { error: 'Order not found' },
        { status: 404 }
      );
    }
    
    // Return status and serial numbers if completed
    const response: any = {
      status: order.status,
      tx_hash: order.tx_hash
    };
    
    if (order.status === 'completed') {
      response.serial_numbers = order.serial_numbers;
    }
    
    return NextResponse.json(response);
    
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}