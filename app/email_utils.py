import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def send_email(to_email, subject, body):
    try:
        sender_email = os.environ.get("SMTP_EMAIL")
        sender_password = os.environ.get("SMTP_PASSWORD")

        if not sender_email or not sender_password:
            print(" Missing SMTP credentials in .env file.")
            return

        msg = MIMEMultipart()
        msg["From"] = f"S_App <{sender_email}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print(f" Email sent to {to_email}")

    except Exception as e:
        print(f" Error sending email: {e}")
