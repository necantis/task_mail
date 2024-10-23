import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(recipient_email: str, subject: str, body: str) -> None:
    """Send email using SMTP with proper error handling."""
    smtp_username = os.environ.get('SMTP_USERNAME')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    
    if not smtp_username or not smtp_password:
        raise ValueError("SMTP credentials not configured")
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # Connect to SMTP server (using Gmail SMTP)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(smtp_username, smtp_password)
        
        # Send email
        server.send_message(msg)
        server.quit()
    except smtplib.SMTPAuthenticationError:
        raise ValueError("Failed to authenticate with SMTP server")
    except smtplib.SMTPException as e:
        raise ValueError(f"Failed to send email: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error while sending email: {str(e)}")
