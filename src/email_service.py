import os
import re
import time
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EnterpriseEmailService:
    """SMTP Pipeline supporting single-dispatch BCC payloads for secure document distribution."""

    @staticmethod
    def _clean_emails(raw_value: str) -> list[str]:
        """Extract and sanitize all valid email addresses from comma/newline-separated text."""
        if not raw_value:
            return []
        # Split by commas, semicolons, or whitespace/newlines
        tokens = re.split(r"[,;\s]+", str(raw_value).strip())
        cleaned = []
        seen = set()
        for token in tokens:
            addr = token.strip().strip('"').strip("'")
            if "@" in addr and "." in addr.split("@")[-1]:
                lower_addr = addr.lower()
                if lower_addr not in seen:
                    seen.add(lower_addr)
                    cleaned.append(addr)
        return cleaned

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

        clean_sender = sender_email.strip().strip('"').strip("'")
        clean_password = app_password.strip().strip('"').strip("'")

        if "@" not in clean_sender:
            raise ValueError(f"Invalid sender email format: {clean_sender}")

        recipient_list = EnterpriseEmailService._clean_emails(recipient_string)
        if not recipient_list:
            raise ValueError("No valid recipient email addresses found in Secrets.")

        email_subject = subject or "Automated Executive Briefing: Nifty 500 Market Matrix"
        email_body = body or "Team,\n\nPlease find attached the automated tracking matrix report."

        # Build ONE single email message for all recipients (BCC privacy)
        msg = MIMEMultipart()
        msg["From"] = clean_sender
        msg["To"] = clean_sender
        msg["Subject"] = email_subject

        msg.attach(MIMEText(email_body, "plain"))

        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
            part["Content-Disposition"] = f'attachment; filename="{os.path.basename(attachment_path)}"'
            msg.attach(part)

        # Send single email to all recipients with automatic retry for Streamlit Cloud DNS
        smtp_host = "://gmail.com"
        smtp_port = 587
        last_error = None

        for attempt in range(3):
            server = None
            try:
                server = smtplib.SMTP(smtp_host, smtp_port, timeout=25)
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(clean_sender, clean_password)
                server.sendmail(clean_sender, recipient_list, msg.as_string())
                return len(recipient_list)
            except Exception as err:
                last_error = err
                if attempt < 2:
                    time.sleep(2)
            finally:
                if server is not None:
                    try:
                        server.quit()
                    except Exception:
                        pass

        raise RuntimeError(f"SMTP dispatch failed after 3 attempts: {last_error}")
