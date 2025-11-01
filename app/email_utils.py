import os
import requests
import traceback

def send_email(to_email, subject, message):
    sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("FROM_EMAIL")

    if not sendgrid_api_key or not from_email:
        print("⚠️ [Email Warning] Missing SENDGRID_API_KEY or FROM_EMAIL environment variable.")
        return False

    data = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": from_email},
        "subject": subject,
        "content": [{"type": "text/plain", "value": message}],
    }

    try:
        response = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {sendgrid_api_key}",
                "Content-Type": "application/json",
            },
            json=data,
            timeout=10
        )

        if response.status_code >= 400:
            print(f"⚠️ [Email Error] SendGrid returned {response.status_code}: {response.text}")
            return False

        print(f"✅ Email sent successfully to {to_email}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"⚠️ [Email Warning] Network error sending email: {e}")
        return False

    except Exception as e:
        print(f"⚠️ [Email Warning] Unexpected error sending email: {e}")
        traceback.print_exc()
        return False
