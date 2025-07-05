#!/usr/bin/env python3
"""Simple test script for email service."""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.email import email_service
from app.config import settings


async def test_email_service():
    """Test the email service functionality."""
    print("Testing Ultra Civic Email Service")
    print("=" * 40)
    
    # Test basic email sending
    print("\n1. Testing basic email functionality...")
    try:
        result = await email_service.send_email(
            to=settings.alert_email,
            subject="Test Email from Ultra Civic",
            html_content="<h1>Test Email</h1><p>This is a test email to verify the email service is working.</p>",
            text_content="Test Email\n\nThis is a test email to verify the email service is working.",
            tags=["test"]
        )
        
        if result["success"]:
            print(f"✅ Basic email sent successfully: {result.get('email_id')}")
        else:
            print(f"❌ Basic email failed: {result.get('error')}")
    except Exception as e:
        print(f"❌ Basic email exception: {str(e)}")
    
    # Test admin alert
    print("\n2. Testing admin alert functionality...")
    try:
        result = await email_service.send_admin_alert(
            alert_type="test_alert",
            message="This is a test alert to verify admin notifications work correctly.",
            details={
                "test_parameter": "test_value",
                "timestamp": "2024-01-01T00:00:00Z",
                "system_status": "testing"
            },
            urgency="medium"
        )
        
        if result["success"]:
            print(f"✅ Admin alert sent successfully: {result.get('email_id')}")
        else:
            print(f"❌ Admin alert failed: {result.get('error')}")
    except Exception as e:
        print(f"❌ Admin alert exception: {str(e)}")
    
    # Test token transfer failure alert
    print("\n3. Testing token transfer failure alert...")
    try:
        result = await email_service.send_token_transfer_failure_alert(
            order_id="test-order-123",
            wallet_address="0x1234567890abcdef1234567890abcdef12345678",
            num_allowances=5,
            error_details="Test error: API timeout",
            thirdweb_response={"error": "timeout", "code": 408}
        )
        
        if result["success"]:
            print(f"✅ Token transfer failure alert sent successfully: {result.get('email_id')}")
        else:
            print(f"❌ Token transfer failure alert failed: {result.get('error')}")
    except Exception as e:
        print(f"❌ Token transfer failure alert exception: {str(e)}")
    
    # Test system error alert
    print("\n4. Testing system error alert...")
    try:
        result = await email_service.send_system_error_alert(
            error_type="database_connection_error",
            error_message="Unable to connect to PostgreSQL database",
            context={
                "database_url": "postgresql://***hidden***",
                "retry_count": 3,
                "last_error": "Connection timeout"
            }
        )
        
        if result["success"]:
            print(f"✅ System error alert sent successfully: {result.get('email_id')}")
        else:
            print(f"❌ System error alert failed: {result.get('error')}")
    except Exception as e:
        print(f"❌ System error alert exception: {str(e)}")
    
    print("\n" + "=" * 40)
    print("Email service testing completed!")
    print(f"Admin email: {settings.alert_email}")
    print(f"Resend API key configured: {'Yes' if settings.resend_api_key else 'No'}")


if __name__ == "__main__":
    asyncio.run(test_email_service())