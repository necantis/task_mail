import os
import smtplib
import re
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_email(email: str) -> bool:
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def send_email(recipient_email: str, subject: str, body: str) -> None:
    """Send email using SMTP with enhanced error handling and validation."""
    # Validate credentials
    smtp_username = os.environ.get('SMTP_USERNAME')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    
    if not smtp_username or not smtp_password:
        raise ValueError("SMTP credentials not configured")
    
    # Validate email address
    if not validate_email(recipient_email):
        raise ValueError(f"Invalid recipient email address: {recipient_email}")
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    server = None
    try:
        # Connect to SMTP server with enhanced configuration
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()  # Initial EHLO
        server.starttls()  # Enable TLS
        server.ehlo()  # Second EHLO after TLS
        
        # Attempt login
        try:
            server.login(smtp_username, smtp_password)
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed")
            raise ValueError("Failed to authenticate with SMTP server. Please check your credentials.")
        
        # Send email
        try:
            server.send_message(msg)
            logger.info(f"Email sent successfully to {recipient_email}")
        except smtplib.SMTPRecipientsRefused:
            logger.error(f"Recipient refused: {recipient_email}")
            raise ValueError("Email was refused by recipient server")
        except smtplib.SMTPSenderRefused:
            logger.error("Sender address refused")
            raise ValueError("Sender email address was refused")
        except smtplib.SMTPDataError as e:
            logger.error(f"SMTP data error: {str(e)}")
            raise ValueError(f"Error sending email data: {str(e)}")
        
    except smtplib.SMTPConnectError:
        logger.error("Failed to connect to SMTP server")
        raise ValueError("Could not connect to email server")
    except smtplib.SMTPServerDisconnected:
        logger.error("Server disconnected unexpectedly")
        raise ValueError("Email server disconnected unexpectedly")
    except Exception as e:
        logger.error(f"Unexpected error while sending email: {str(e)}")
        raise ValueError(f"Failed to send email: {str(e)}")
    finally:
        # Ensure server is properly closed
        if server is not None:
            try:
                server.quit()
            except Exception as e:
                logger.warning(f"Error while closing SMTP connection: {str(e)}")
