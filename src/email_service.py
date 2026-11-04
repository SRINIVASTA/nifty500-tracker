import os
import time
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EnterpriseEmailService:
    """SMTP Pipeline supporting multi-part payloads for secure document distribution."""
    
    @staticmethod
    def send_report(recipient_string: str, attachment_path: str, sender_email: str, app_password: str, subject: str = None, body: str = None):
        if not os.path.exists(attachment_path):
            raise FileNotFoundError(f"Attachment target missing: {attachment_path}")

        recipient_list = [email.strip() for email in recipient_string.split(",") if email.strip()]
        if not recipient_list:
            raise ValueError("No valid recipient email addresses found.")

        email_subject = subject or "Automated Executive Briefing: Nifty 500 Market Matrix"
        email_body = body or "Team,\n\nPlease find attached the automated tracking matrix report."

        # Fixed: Corrected malformed SMTP connection target string
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, app_password)

        for index, receiver in enumerate(recipient_list):
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver
            msg['Subject'] = email_subject
            
            msg.attach(MIMEText(email_body, 'plain'))

            with open(attachment_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
                msg.attach(part)

            server.sendmail(sender_email, receiver, msg.as_string())
            
            if len(recipient_list) > 1 and index < len(recipient_list) - 1:
                time.sleep(1)

        server.quit()
        return len(recipient_list)
