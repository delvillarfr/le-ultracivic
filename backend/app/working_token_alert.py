#!/usr/bin/env python3
"""Test token alert using exact format that works."""

import asyncio
import httpx
from app.config import settings


async def test_working_token_alert():
    """Test token alert using the exact same format as our working simple email."""
    
    # Use exact same format as working simple test
    payload = {
        "from": "noreply@ultracivic.com",
        "to": ["paco@ultracivic.com"],
        "subject": "Token Transfer Failed - Order test-789",
        "html": "<h1>Token Transfer Failed</h1><p>Order: test-789</p><p>Wallet: 0x1234...5678</p><p>Allowances: 5</p>",
        "text": "Token Transfer Failed\n\nOrder: test-789\nWallet: 0x1234...5678\nAllowances: 5"
    }
    
    print("Testing working token alert format:")
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
            print(f"✅ Token alert sent successfully: {result.get('id')}")
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_working_token_alert())
    if success:
        print("\n🎉 Token transfer alerts are working!")
    else:
        print("\n❌ Still debugging the alert format.")