import smtplib
import os

from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()


def send_email_alert(
    subject,
    body,
    recipients
):

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = os.getenv("EMAIL_USER")

    msg["To"] = ", ".join(
        recipients
    )

    with smtplib.SMTP(
        os.getenv("EMAIL_HOST"),
        int(os.getenv("EMAIL_PORT"))
    ) as server:

        server.starttls()

        server.login(
            os.getenv("EMAIL_USER"),
            os.getenv("EMAIL_PASSWORD")
        )

        server.sendmail(
            os.getenv("EMAIL_USER"),
            recipients,
            msg.as_string()
        )