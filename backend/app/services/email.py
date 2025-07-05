"""Email service using Resend for admin notifications."""

import logging
from typing import Dict, Optional, List
from datetime import datetime
import json

import httpx
from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails using Resend API."""

    def __init__(self):
        self.api_key = settings.resend_api_key
        self.api_url = "https://api.resend.com/emails"
        self.from_email = "noreply@ultracivic.com"
        self.admin_email = settings.alert_email
        
        # Rate limiting to prevent spam
        self.max_emails_per_hour = 50
        self.email_history = []

    async def send_email(
        self,
        to: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """
        Send an email using Resend API.
        
        Args:
            to: Recipient email address
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text email content (optional)
            tags: Email tags for categorization
            
        Returns:
            Dict with send result
        """
        try:
            # Check rate limiting
            if not self._check_rate_limit():
                return {
                    "success": False,
                    "error": "Rate limit exceeded for email sending"
                }

            # Validate inputs
            if not to or not subject or not html_content:
                return {
                    "success": False,
                    "error": "Missing required email fields (to, subject, or html_content)"
                }
            
            # Clean the HTML content to remove any problematic characters
            clean_html = html_content.replace('\x00', '').replace('\r\n', '\n').replace('\r', '\n')
            clean_text = text_content.replace('\x00', '').replace('\r\n', '\n').replace('\r', '\n') if text_content else None
            
            # Prepare email payload
            payload = {
                "from": self.from_email,
                "to": [to],
                "subject": subject,
                "html": clean_html
            }
            
            if clean_text:
                payload["text"] = clean_text
                
            if tags:
                payload["tags"] = [tag for tag in tags if tag]  # Filter out empty tags

            # Debug: Log the payload for troubleshooting
            logger.debug(f"Email payload: {json.dumps(payload, indent=2)}")
            
            # Send email via Resend API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=30
                )

            # Track email send for rate limiting
            self._track_email_send()

            if response.status_code == 200:
                result = response.json()
                logger.info(f"Email sent successfully to {to}, ID: {result.get('id')}")
                return {
                    "success": True,
                    "message": "Email sent successfully",
                    "email_id": result.get("id"),
                    "details": {
                        "to": to,
                        "subject": subject,
                        "sent_at": datetime.now().isoformat()
                    }
                }
            else:
                error_msg = f"Failed to send email: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code
                }

        except httpx.TimeoutException:
            error_msg = "Email send timeout"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Email send error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    async def send_admin_alert(
        self,
        alert_type: str,
        message: str,
        details: Optional[Dict] = None,
        urgency: str = "medium"
    ) -> Dict[str, any]:
        """
        Send an alert email to admin.
        
        Args:
            alert_type: Type of alert (e.g., "token_transfer_failed")
            message: Alert message
            details: Additional details dictionary
            urgency: Alert urgency level (low, medium, high, critical)
            
        Returns:
            Dict with send result
        """
        try:
            # Generate subject based on urgency
            urgency_prefix = {
                "low": "📝",
                "medium": "⚠️",
                "high": "🚨",
                "critical": "🔥"
            }.get(urgency, "⚠️")
            
            subject = f"{urgency_prefix} Ultra Civic Alert: {alert_type.replace('_', ' ').title()}"
            
            # Generate email content
            html_content = self._generate_alert_html(alert_type, message, details, urgency)
            text_content = self._generate_alert_text(alert_type, message, details, urgency)
            
            # Send email
            result = await self.send_email(
                to=self.admin_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                tags=["alert", alert_type, urgency]
            )
            
            if result["success"]:
                logger.info(f"Admin alert sent successfully: {alert_type}")
            else:
                logger.error(f"Failed to send admin alert: {result.get('error')}")
                
            return result
            
        except Exception as e:
            error_msg = f"Admin alert error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    async def send_token_transfer_failure_alert(
        self,
        order_id: str,
        wallet_address: str,
        num_allowances: int,
        error_details: str,
        thirdweb_response: Optional[Dict] = None
    ) -> Dict[str, any]:
        """
        Send simple alert for token transfer failures.
        
        Args:
            order_id: Order ID that failed
            wallet_address: User's wallet address
            num_allowances: Number of allowances
            error_details: Error description
            thirdweb_response: Raw Thirdweb response
            
        Returns:
            Dict with send result
        """
        try:
            # Create simple email content
            subject = f"Token Transfer Failed - Order {order_id}"
            
            html_content = f"""<html>
<body>
<h1>Token Transfer Failed</h1>
<p><strong>Order:</strong> {order_id}</p>
<p><strong>Wallet:</strong> {wallet_address}</p>
<p><strong>Allowances:</strong> {num_allowances}</p>
<p><strong>Error:</strong> {error_details}</p>
<p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
<p>Manual intervention required to complete token distribution.</p>
<p>---<br>Ultra Civic System</p>
</body>
</html>"""
            
            text_content = f"""Token Transfer Failed

Order: {order_id}
Wallet: {wallet_address}
Allowances: {num_allowances}
Error: {error_details}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

Manual intervention required to complete token distribution.

---
Ultra Civic System"""
            
            # Send simple email directly
            return await self.send_email(
                to=self.admin_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                tags=["alert", "token_transfer_failed", "high"]
            )
            
        except Exception as e:
            error_msg = f"Token transfer failure alert error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    async def send_system_error_alert(
        self,
        error_type: str,
        error_message: str,
        context: Optional[Dict] = None
    ) -> Dict[str, any]:
        """
        Send alert for system errors.
        
        Args:
            error_type: Type of error
            error_message: Error message
            context: Additional context
            
        Returns:
            Dict with send result
        """
        try:
            details = {
                "error_type": error_type,
                "error_message": error_message,
                "context": context or {},
                "timestamp": datetime.now().isoformat()
            }
            
            message = f"""
            System error occurred: {error_type}
            
            Error: {error_message}
            
            Please investigate and resolve the issue.
            """
            
            return await self.send_admin_alert(
                alert_type="system_error",
                message=message,
                details=details,
                urgency="high"
            )
            
        except Exception as e:
            error_msg = f"System error alert error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        try:
            current_time = datetime.now()
            
            # Remove emails older than 1 hour
            self.email_history = [
                email_time for email_time in self.email_history
                if (current_time - email_time).total_seconds() < 3600
            ]
            
            # Check if we're under the limit
            return len(self.email_history) < self.max_emails_per_hour
            
        except Exception as e:
            logger.error(f"Rate limit check error: {str(e)}")
            return True  # Allow email on error

    def _track_email_send(self):
        """Track email send time for rate limiting."""
        try:
            self.email_history.append(datetime.now())
        except Exception as e:
            logger.error(f"Email tracking error: {str(e)}")

    def _generate_alert_html(
        self,
        alert_type: str,
        message: str,
        details: Optional[Dict],
        urgency: str
    ) -> str:
        """Generate simple HTML content for alert email."""
        try:
            # Clean and escape message content
            clean_message = message.strip().replace('<', '&lt;').replace('>', '&gt;')
            clean_alert_type = alert_type.replace('_', ' ').title()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
            
            html = f"""<html>
<body>
<h1>Ultra Civic Alert</h1>
<p><strong>Type:</strong> {clean_alert_type}</p>
<p><strong>Urgency:</strong> {urgency.upper()}</p>
<p><strong>Time:</strong> {timestamp}</p>
<h2>Message</h2>
<p>{clean_message}</p>"""
            
            # Add simple details if present
            if details:
                html += "<h2>Details</h2><ul>"
                for key, value in details.items():
                    clean_key = key.replace('_', ' ').title()
                    clean_value = str(value).replace('<', '&lt;').replace('>', '&gt;')
                    html += f"<li><strong>{clean_key}:</strong> {clean_value}</li>"
                html += "</ul>"
            
            html += """<p>---<br>Ultra Civic System</p>
</body>
</html>"""
            
            return html
            
        except Exception as e:
            logger.error(f"HTML generation error: {str(e)}")
            return f"<html><body><h1>Alert</h1><p>{alert_type}: {message}</p></body></html>"

    def _format_details_html(self, details: Dict) -> str:
        """Format details dictionary as HTML."""
        try:
            html = "<h2>Details</h2><div class='details'>"
            
            for key, value in details.items():
                key_display = key.replace('_', ' ').title()
                if isinstance(value, dict):
                    html += f"<strong>{key_display}:</strong><br>"
                    # Convert dict to simple string representation instead of JSON
                    dict_str = ", ".join([f"{k}: {v}" for k, v in value.items()])
                    html += f"<code>{dict_str}</code><br>"
                else:
                    # Escape any problematic characters
                    value_str = str(value).replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
                    html += f"<strong>{key_display}:</strong> {value_str}<br>"
            
            html += "</div>"
            return html
            
        except Exception as e:
            logger.error(f"Details formatting error: {str(e)}")
            return "<div class='details'>Error formatting details</div>"

    def _generate_alert_text(
        self,
        alert_type: str,
        message: str,
        details: Optional[Dict],
        urgency: str
    ) -> str:
        """Generate simple plain text content for alert email."""
        try:
            clean_alert_type = alert_type.replace('_', ' ').title()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
            
            text = f"""ULTRA CIVIC ALERT

Type: {clean_alert_type}
Urgency: {urgency.upper()}
Time: {timestamp}

MESSAGE:
{message.strip()}

"""
            
            if details:
                text += "DETAILS:\n"
                for key, value in details.items():
                    key_display = key.replace('_', ' ').title()
                    text += f"{key_display}: {value}\n"
            
            text += "\n---\nUltra Civic System"
            
            return text
            
        except Exception as e:
            logger.error(f"Text generation error: {str(e)}")
            return f"Alert: {alert_type}\n{message}"


# Global instance
email_service = EmailService()