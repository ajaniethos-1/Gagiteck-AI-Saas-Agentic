"""AWS SES email service."""

import logging
from typing import Optional
import boto3
from botocore.exceptions import ClientError

from api.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """AWS SES email service for sending transactional emails."""

    def __init__(
        self,
        region: str = "us-east-1",
        sender_email: Optional[str] = None,
    ):
        self.region = region
        self.sender_email = sender_email or settings.SES_SENDER_EMAIL
        self._client = None

    def _get_client(self):
        """Get or create SES client."""
        if self._client is None:
            self._client = boto3.client("ses", region_name=self.region)
        return self._client

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> bool:
        """Send an email via SES."""
        try:
            client = self._get_client()

            body = {"Html": {"Charset": "UTF-8", "Data": html_body}}
            if text_body:
                body["Text"] = {"Charset": "UTF-8", "Data": text_body}

            response = client.send_email(
                Source=self.sender_email,
                Destination={"ToAddresses": [to_email]},
                Message={
                    "Subject": {"Charset": "UTF-8", "Data": subject},
                    "Body": body,
                },
            )

            logger.info(f"Email sent to {to_email}, MessageId: {response['MessageId']}")
            return True

        except ClientError as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    async def send_welcome_email(self, to_email: str, name: str) -> bool:
        """Send welcome email to new user."""
        subject = "Welcome to Gagiteck!"
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px; text-align: center;">
                <h1 style="color: white; margin: 0;">Welcome to Gagiteck!</h1>
            </div>
            <div style="padding: 40px; background: #f9fafb;">
                <p>Hi {name},</p>
                <p>Thanks for joining Gagiteck! We're excited to have you on board.</p>
                <p>With Gagiteck, you can:</p>
                <ul>
                    <li>Create and manage AI agents</li>
                    <li>Build automated workflows</li>
                    <li>Monitor executions in real-time</li>
                </ul>
                <p>Get started by visiting your <a href="https://app.mimoai.co">dashboard</a>.</p>
                <p>Best regards,<br>The Gagiteck Team</p>
            </div>
            <div style="padding: 20px; text-align: center; color: #6b7280; font-size: 12px;">
                <p>&copy; 2024 Gagiteck. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        text_body = f"""
        Welcome to Gagiteck!

        Hi {name},

        Thanks for joining Gagiteck! We're excited to have you on board.

        Get started at: https://app.mimoai.co

        Best regards,
        The Gagiteck Team
        """
        return await self.send_email(to_email, subject, html_body, text_body)

    async def send_password_reset_email(
        self,
        to_email: str,
        name: str,
        reset_token: str,
    ) -> bool:
        """Send password reset email."""
        reset_url = f"https://app.mimoai.co/auth/reset-password?token={reset_token}"
        subject = "Reset Your Gagiteck Password"
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px; text-align: center;">
                <h1 style="color: white; margin: 0;">Password Reset</h1>
            </div>
            <div style="padding: 40px; background: #f9fafb;">
                <p>Hi {name},</p>
                <p>We received a request to reset your password. Click the button below to set a new password:</p>
                <p style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block;">Reset Password</a>
                </p>
                <p style="color: #6b7280; font-size: 14px;">This link will expire in 1 hour. If you didn't request a password reset, you can safely ignore this email.</p>
                <p>Best regards,<br>The Gagiteck Team</p>
            </div>
        </body>
        </html>
        """
        text_body = f"""
        Password Reset

        Hi {name},

        We received a request to reset your password. Visit this link to set a new password:
        {reset_url}

        This link will expire in 1 hour. If you didn't request a password reset, you can safely ignore this email.

        Best regards,
        The Gagiteck Team
        """
        return await self.send_email(to_email, subject, html_body, text_body)

    async def send_execution_failure_alert(
        self,
        to_email: str,
        execution_id: str,
        execution_type: str,
        resource_name: str,
        error_message: str,
    ) -> bool:
        """Send execution failure alert email."""
        subject = f"[Alert] {execution_type.capitalize()} Execution Failed"
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #dc2626; padding: 40px; text-align: center;">
                <h1 style="color: white; margin: 0;">Execution Failed</h1>
            </div>
            <div style="padding: 40px; background: #f9fafb;">
                <p>An execution has failed and requires your attention.</p>
                <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin: 20px 0;">
                    <p><strong>Execution ID:</strong> {execution_id}</p>
                    <p><strong>Type:</strong> {execution_type.capitalize()}</p>
                    <p><strong>Resource:</strong> {resource_name}</p>
                    <p><strong>Error:</strong></p>
                    <pre style="background: #fef2f2; padding: 10px; border-radius: 4px; overflow-x: auto;">{error_message}</pre>
                </div>
                <p><a href="https://app.mimoai.co/executions/{execution_id}">View Execution Details</a></p>
            </div>
        </body>
        </html>
        """
        return await self.send_email(to_email, subject, html_body)


# Global email service instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get email service instance."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
