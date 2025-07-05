import { NextRequest, NextResponse } from 'next/server';
import { v4 as uuidv4 } from 'uuid';
import { db } from '@/lib/database';
import { blockchain } from '@/lib/blockchain';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { num_allowances, message, wallet } = body;
    
    // Validation
    if (!num_allowances || typeof num_allowances !== 'number' || num_allowances < 1 || num_allowances > 99) {
      return NextResponse.json(
        { error: 'num_allowances must be a number between 1 and 99' },
        { status: 400 }
      );
    }
    
    if (!message || typeof message !== 'string' || message.length > 100) {
      return NextResponse.json(
        { error: 'message must be a string with max 100 characters' },
        { status: 400 }
      );
    }
    
    if (!wallet || !blockchain.isValidAddress(wallet)) {
      return NextResponse.json(
        { error: 'wallet must be a valid Ethereum address' },
        { status: 400 }
      );
    }
    
    // Generate order ID
    const order_id = uuidv4();
    
    // Reserve allowances
    try {
      const serial_numbers = await db.reserveAllowances(num_allowances, wallet, message, order_id);
      
      return NextResponse.json({
        order_id,
        serial_numbers
      });
    } catch (error) {
      return NextResponse.json(
        { error: (error as Error).message },
        { status: 409 }
      );
    }
    
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}