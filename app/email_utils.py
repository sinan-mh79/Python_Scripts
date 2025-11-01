import smtplib
from email.mime.text import MIMEText
import os

def send_email(to_email, subject, message):
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = smtp_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_email, smtp_pass)
            server.send_message(msg)
            print(f"Email sent to {to_email}")
    except Exception as e:
        print(f" Error sending email: {e}")
