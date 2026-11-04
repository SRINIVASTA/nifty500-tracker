import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EnterpriseEmailService:
    """SMTP Pipeline supporting multi-part payloads for secure document distribution."""
    
    @staticmethod
    def send_report(recipient_email: str, attachment_path: str, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str):
        if not os.path.exists(attachment_path):
            raise FileNotFoundError(f"Attachment target missing: {attachment_path}")

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = "Automated Executive Briefing: Nifty 500 Market Matrix"

        body = (
            "Team,\n\nPlease find attached the automated cryptographic compliance ledger "
            "tracking the daily delta shifts across all Nifty 500 index constituents.\n\n"
            "System Automated Broadcast Engine."
        )
        msg.attach(MIMEText(body, "plain"))

        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
            part["Content-Disposition"] = f'attachment; filename="{os.path.basename(attachment_path)}"'
            msg.attach(part)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
