import os
import time
import smtplib
from pathlib import Path
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EnterpriseEmailService:
    """SMTP Pipeline supporting multi-part payloads for secure document distribution."""

    @staticmethod
    def send_report(
        recipient_string: str,
        attachment_path: str,
        sender_email: str,
        app_password: str,
        subject: str = None,
        body: str = None,
    ):
        if not os.path.exists(attachment_path):
            raise FileNotFoundError(f"Attachment target missing: {attachment_path}")

        recipient_list = [email.strip() for email in recipient_string.split(",") if email.strip()]
        if not recipient_list:
            raise ValueError("No valid recipient email addresses found.")

        email_subject = subject or "Automated Executive Briefing: Global Exchanges Market Matrix"
        email_body = body or "Team,\n\nPlease find attached the automated Global Stock Exchanges & Indices tracking matrix report."

        clean_sender = sender_email.strip()
        clean_password = app_password.replace(" ", "").strip()

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(clean_sender, clean_password)

        for index, receiver in enumerate(recipient_list):
            msg = MIMEMultipart()
            msg["From"] = clean_sender
            msg["To"] = receiver
            msg["Subject"] = email_subject

            msg.attach(MIMEText(email_body, "plain"))

            with open(attachment_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
                part["Content-Disposition"] = f'attachment; filename="{os.path.basename(attachment_path)}"'
                msg.attach(part)

            server.sendmail(clean_sender, receiver, msg.as_string())

            if len(recipient_list) > 1 and index < len(recipient_list) - 1:
                time.sleep(1)

        server.quit()
        return len(recipient_list)


def send_report_email(pdf_path: Path, secrets_dict: dict | None = None) -> tuple[bool, str]:
    """Bridge helper connecting Streamlit secrets and GitHub Actions env vars to EnterpriseEmailService."""
    cfg = secrets_dict or {}

    sender = cfg.get("username") or cfg.get("sender_email") or os.getenv("SENDER_EMAIL")
    password = cfg.get("app_password") or os.getenv("APP_PASSWORD")
    raw_recipients = cfg.get("to_email") or cfg.get("recipients") or os.getenv("RECIPIENTS", "")

    if isinstance(raw_recipients, list):
        recipient_string = ", ".join(str(r).strip() for r in raw_recipients if str(r).strip())
    else:
        recipient_string = str(raw_recipients).strip()

    if not sender or not password or not recipient_string:
        return False, "Missing SMTP credentials (username, app_password, or to_email)."

    try:
        sent_count = EnterpriseEmailService.send_report(
            recipient_string=recipient_string,
            attachment_path=str(pdf_path),
            sender_email=str(sender),
            app_password=str(password),
        )
        return True, f"Dispatched PDF report to {sent_count} recipient(s)."
    except Exception as e:
        return False, f"SMTP Error: {e}"
