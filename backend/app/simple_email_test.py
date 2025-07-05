#!/usr/bin/env python3
"""Simple email test to isolate the validation issue."""

import asyncio
import httpx
import json
from app.config import settings


async def test_simple_email():
    """Test with minimal email payload to isolate the issue."""
    
    # Simple test payload
    payload = {
        "from": "noreply@ultracivic.com",
        "to": ["paco@ultracivic.com"],
        "subject": "Simple Test",
        "html": "<h1>Test</h1><p>Simple test email.</p>",
        "text": "Test\n\nSimple test email."
    }
    
    print("Testing simple email payload:")
    print(json.dumps(payload, indent=2))
    
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
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Simple email sent successfully!")
        else:
            print(f"❌ Simple email failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_simple_email())