# email_utils.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage



def send_email(to_email, subject, body):
    print("Sending to:", to_email)  # DEBUG
    SENDER_EMAIL = "apoorvg497@gmail.com"
    EMAIL_PASSWORD = "anrx zrvu xvcc hykd"  # Use App Password if using Gmail with 2FA

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER_EMAIL, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("Email sent to", to_email)  # DEBUG
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
