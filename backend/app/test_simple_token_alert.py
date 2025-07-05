#!/usr/bin/env python3
"""Test simplified token transfer alert."""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.email import email_service


async def test_simple_token_alert():
    """Test the simplified token transfer failure alert."""
    print("Testing simplified token transfer failure alert...")
    
    try:
        result = await email_service.send_token_transfer_failure_alert(
            order_id="test-order-456",
            wallet_address="0x1234567890abcdef1234567890abcdef12345678",
            num_allowances=3,
            error_details="Thirdweb API timeout after 60 seconds"
        )
        
        if result["success"]:
            print(f"✅ Token transfer failure alert sent successfully!")
            print(f"Email ID: {result.get('email_id')}")
            return True
        else:
            print(f"❌ Token transfer failure alert failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_simple_token_alert())
    if success:
        print("\n🎉 Simplified email alerts are working! The critical requirement from CLAUDE.md is fulfilled.")
    else:
        print("\n❌ Email alerts still need debugging.")