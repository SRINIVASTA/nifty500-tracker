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

        # Clean and convert the input string into a proper Python list
        recipient_list = [email.strip() for email in recipient_string.split(",") if email.strip()]
        if not recipient_list:
            raise ValueError("No valid recipient email addresses found.")

        # Default contents if not custom-defined by the workspace UI
        email_subject = subject or "Automated Executive Briefing: Nifty 500 Market Matrix"
        email_body = body or (
            "Team,\n\nPlease find attached the automated compliance ledger "
            "tracking the daily delta shifts across all Nifty 500 index constituents.\n\n"
            "System Automated Broadcast Engine."
        )

        # Establish secure connection to Gmail
        server = smtplib.SMTP('://gmail.com', 587)
        server.starttls()
        server.login(sender_email, app_password)

        # Loop through each recipient and send individually
        for index, receiver in enumerate(recipient_list):
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver
            msg['Subject'] = email_subject
            
            # Attach plain-text body copy
            msg.attach(MIMEText(email_body, 'plain'))

            # Read and inject the physical PDF binary stream payload
            with open(attachment_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
                msg.attach(part)

            # Route out the constructed email packet
            server.sendmail(sender_email, receiver, msg.as_string())
            
            # Anti-spam delay: sleep for 1 second if sending to multiple people
            if len(recipient_list) > 1 and index < len(recipient_list) - 1:
                time.sleep(1)

        server.quit()
        return len(recipient_list)
