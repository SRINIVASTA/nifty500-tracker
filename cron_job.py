#!/usr/bin/env python3
import os
import sys
import logging
from datetime import date, timedelta

from src.data_engine import NiftyDataEngine
from src.pdf_generator import NiftyPDFGenerator
from src.email_service import EnterpriseEmailService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("pipeline_automation.log"),
        logging.StreamHandler()
    ]
)

def _load_credentials() -> tuple[str, str, str]:
    """Read credentials from GitHub Actions env vars first, then fallback to local secrets.toml."""
    sender = os.getenv("EMAIL_USERNAME", "").strip()
    password = os.getenv("EMAIL_APP_PASSWORD", "").strip()
    recipients = os.getenv("EMAIL_TO", "").strip()

    if sender and password and recipients:
        logging.info("✓ Credentials loaded from environment variables.")
        return sender, password, recipients

    secrets_path = os.path.join(".streamlit", "secrets.toml")
    if os.path.exists(secrets_path):
        try:
            import toml
            secrets = toml.load(secrets_path)
            sender = sender or str(secrets["gmail"].get("username", "")).strip()
            password = password or str(secrets["gmail"].get("app_password", "")).strip()
            raw_to = recipients or secrets["gmail"].get("to_email", "")
            if isinstance(raw_to, list):
                recipients = ", ".join(str(r).strip() for r in raw_to if str(r).strip())
            else:
                recipients = str(raw_to).strip()
            logging.info("✓ Credentials loaded from local Streamlit secrets file.")
        except Exception as err:
            logging.error(f"❌ Failed to parse secrets.toml: {err}")

    return sender, password, recipients

def run_unattended_pipeline():
    logging.info("🚀 Initializing Streamlit-Linked Market Matrix Pipeline...")

    end_date = date.today()
    start_date = end_date - timedelta(days=3)

    sender_email, app_password, recipient_list = _load_credentials()
    if not (sender_email and app_password and recipient_list):
        logging.error("❌ Aborted: Missing SMTP credentials in both GitHub Secrets and secrets.toml.")
        sys.exit(1)

    output_pdf = "Nifty500_Automated_Briefing.pdf"

    try:
        engine = NiftyDataEngine()
        master_list = engine.fetch_master_list()

        logging.info(f"Evaluating absolute price changes from {start_date} to {end_date}...")
        processed_df = engine.process_daily_performance(master_list, start_date, end_date)

        if processed_df.empty:
            logging.error("❌ Data Engine returned an empty matrix payload.")
            sys.exit(1)

        logging.info(f"Compiling portrait tracking layout rules into: '{output_pdf}'...")
        NiftyPDFGenerator.generate(processed_df, output_pdf)

        logging.info("Connecting to secure relays and distributing PDF reports...")
        total_sent = EnterpriseEmailService.send_report(
            recipient_string=recipient_list,
            attachment_path=output_pdf,
            sender_email=sender_email,
            app_password=app_password,
            subject=f"Automated Matrix Briefing: Nifty 500 [{end_date.strftime('%Y-%m-%d')}]",
            body=(
                f"Team,\n\n"
                f"Please find attached the automated portrait tracking ledger mapping absolute index delta shifts.\n\n"
                f"Execution Summary Metrics:\n"
                f"- Window Interval Checked: {start_date} to {end_date}\n"
                f"- Tracked Asset Registry Count: {len(processed_df)} Active Listings\n\n"
                f"Best Regards,\n"
                f"Enterprise Automation Engine"
            )
        )
        logging.info(f"🚀 Success! Document payload successfully sent to ({total_sent}) distributions.")

    except Exception as general_error:
        logging.critical(f"❌ Ingestion Pipeline Failure: {str(general_error)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    run_unattended_pipeline()
