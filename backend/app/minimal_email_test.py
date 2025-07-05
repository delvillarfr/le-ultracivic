#!/usr/bin/env python3
"""Minimal email test for token transfer failure alert."""

import asyncio
import httpx
from app.config import settings


async def test_minimal_token_alert():
    """Test minimal token transfer failure alert."""
    
    # Extremely simple payload matching our working simple test
    payload = {
        "from": "noreply@ultracivic.com",
        "to": ["paco@ultracivic.com"],
        "subject": "Token Transfer Failed - Order test-123",
        "html": "<h1>Token Transfer Failed</h1><p>Order: test-123</p><p>Wallet: 0x1234...5678</p><p>Allowances: 5</p><p>Error: API timeout</p>",
        "text": "Token Transfer Failed\n\nOrder: test-123\nWallet: 0x1234...5678\nAllowances: 5\nError: API timeout"
    }
    
    print("Testing minimal token transfer failure alert:")
    print(f"Subject: {payload['subject']}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.resend.com/emails",
                json=payload,
                headers={
                    "Authorization": f"Bearer {settings.resend_api_key}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Minimal token alert sent successfully: {result.get('id')}")
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_minimal_token_alert())
    if success:
        print("\n✅ Minimal email alert is working! The service is ready for production.")
    else:
        print("\n❌ Still having issues with email alerts.")