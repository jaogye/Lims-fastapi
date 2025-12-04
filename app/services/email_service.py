"""
Email service module for sending notifications.

This module provides email functionality for sending password reset notifications
and other system emails using SMTP.
"""

import smtplib
import secrets
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service class for email operations.

    Handles sending emails for password resets and other notifications.
    """

    @staticmethod
    def generate_temp_password(length: int = 12) -> str:
        """
        Generate a secure temporary password.

        Args:
            length (int): Length of the password (default 12).

        Returns:
            str: Randomly generated secure password.
        """
        # Use a mix of uppercase, lowercase, digits, and special characters
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password

    @staticmethod
    async def send_temp_password_email(
        to_email: str,
        username: str,
        temp_password: str,
        user_name: str
    ) -> bool:
        """
        Send temporary password to user's email.

        Args:
            to_email (str): Recipient email address.
            username (str): User's username/code.
            temp_password (str): Temporary password to send.
            user_name (str): User's full name.

        Returns:
            bool: True if email was sent successfully, False otherwise.
        """
        if not settings.SMTP_HOST or not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
            logger.error("SMTP configuration is not complete. Email cannot be sent.")
            return False

        if not to_email:
            logger.error("No email address provided for user.")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Your Temporary Password - LIMS System'
            msg['From'] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL or settings.SMTP_USERNAME}>"
            msg['To'] = to_email

            # Create HTML content
            html_content = f"""
            <html>
              <head></head>
              <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
                  <h2 style="color: #2c3e50;">Password Reset - LIMS System</h2>

                  <p>Hello {user_name},</p>

                  <p>Your password has been reset by an administrator. Below are your temporary login credentials:</p>

                  <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Username:</strong> {username}</p>
                    <p style="margin: 5px 0;"><strong>Temporary Password:</strong> <code style="background-color: #e8e8e8; padding: 2px 6px; border-radius: 3px; font-size: 14px;">{temp_password}</code></p>
                  </div>

                  <p><strong style="color: #e74c3c;">Important:</strong></p>
                  <ul>
                    <li>You will be required to change this password upon your next login</li>
                    <li>This is a temporary password for security reasons</li>
                    <li>Please keep this password confidential</li>
                  </ul>

                  <p>If you did not request this password reset, please contact your system administrator immediately.</p>

                  <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">

                  <p style="font-size: 12px; color: #666;">
                    This is an automated message from the LIMS System. Please do not reply to this email.
                  </p>
                </div>
              </body>
            </html>
            """

            # Create plain text version as fallback
            text_content = f"""
Password Reset - LIMS System

Hello {user_name},

Your password has been reset by an administrator. Below are your temporary login credentials:

Username: {username}
Temporary Password: {temp_password}

IMPORTANT:
- You will be required to change this password upon your next login
- This is a temporary password for security reasons
- Please keep this password confidential

If you did not request this password reset, please contact your system administrator immediately.

---
This is an automated message from the LIMS System. Please do not reply to this email.
            """

            # Attach both HTML and plain text parts
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)

            # Send email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_USE_TLS:
                    server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)

            logger.info(f"Temporary password email sent successfully to {to_email}")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed. Check your email credentials.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error occurred while sending email: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            return False
