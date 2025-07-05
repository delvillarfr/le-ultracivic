import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/database';

export async function GET(request: NextRequest) {
  try {
    // Get all retired allowances for history table
    const retiredAllowances = await db.getRetiredAllowances();
    
    return NextResponse.json({
      retirements: retiredAllowances.map(allowance => ({
        serial_number: allowance.serial_number,
        message: allowance.message,
        wallet: allowance.wallet,
        timestamp: allowance.timestamp
      }))
    });
    
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}