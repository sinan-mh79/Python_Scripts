import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import traceback

def send_email(to_email, subject, message):
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    if not smtp_email or not smtp_password:
        print(" [Email Disabled] Missing SMTP credentials. Email skipped.")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = smtp_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.send_message(msg)

        print(f" Email sent successfully to {to_email}")
        return True

    except smtplib.SMTPException as e:
        print(f" [Email Error] SMTP error: {e}")
        traceback.print_exc()
        return False

    except Exception as e:
        print(f" [Email Error] Unexpected error: {e}")
        traceback.print_exc()
        return False
