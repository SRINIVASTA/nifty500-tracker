import os
import smtplib
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

        email_subject = subject or "Automated Executive Briefing: Nifty 500 Market Matrix"
        email_body = body or "Team,\n\nPlease find attached the automated tracking matrix report."

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = sender_email
        msg["Subject"] = email_subject

        msg.attach(MIMEText(email_body, "plain"))

        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
            part["Content-Disposition"] = f'attachment; filename="{os.path.basename(attachment_path)}"'
            msg.attach(part)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        try:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, recipient_list, msg.as_string())
        finally:
            server.quit()

        return len(recipient_list)
