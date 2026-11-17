#!/usr/bin/env python3
import os
import sys
import logging
from datetime import date, timedelta
from pathlib import Path

from src.data_engine import NiftyDataEngine
from src.pdf_generator import NiftyPDFGenerator
from src.email_service import EnterpriseEmailService

SECRETS_PATH = Path(__file__).resolve().parent / ".streamlit" / "secrets.toml"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("pipeline_automation.log"),
        logging.StreamHandler()
    ]
)

def _load_smtp_credentials() -> tuple[str, str, str]:
    """Exact same credential loader from Global Exchange: GitHub Secrets first, then secrets.toml."""
    sender = os.getenv("USERNAME") or os.getenv("EMAIL_USERNAME") or ""
    password = os.getenv("APP_PASSWORD") or os.getenv("EMAIL_APP_PASSWORD") or ""
    recipients = os.getenv("TO_EMAIL") or os.getenv("EMAIL_TO") or ""

    if (not sender or not password or not recipients) and SECRETS_PATH.exists():
        import toml
        secrets = toml.load(SECRETS_PATH)
        cfg = secrets.get("gmail", secrets)
        sender = sender or str(cfg.get("username", cfg.get("sender_email", "")))
        password = password or str(cfg.get("app_password", ""))
        raw_to = recipients or cfg.get("to_email", cfg.get("recipients", ""))
        if isinstance(raw_to, list):
            recipients = ", ".join(str(r).strip() for r in raw_to if str(r).strip())
        else:
            recipients = str(raw_to)

    return sender.strip(), password.strip(), recipients.strip()

def run_unattended_pipeline():
    logging.info("🚀 Initializing Nifty 500 Market Matrix Pipeline...")

    end_date = date.today()
    start_date = end_date - timedelta(days=3)

    sender_email, app_password, recipient_list = _load_smtp_credentials()
    if not (sender_email and app_password and recipient_list):
        logging.error("❌ Aborted: SMTP credentials not found in GitHub Secrets or secrets.toml.")
        sys.exit(1)

    output_pdf = "Nifty500_Automated_Briefing.pdf"

    try:
        engine = NiftyDataEngine()
        master_list = engine.fetch_master_list()

        logging.info(f"Evaluating price changes from {start_date} to {end_date}...")
        processed_df = engine.process_daily_performance(master_list, start_date, end_date)

        if processed_df.empty:
            logging.error("❌ Data Engine returned an empty matrix payload.")
            sys.exit(1)

        logging.info(f"Compiling PDF report into: '{output_pdf}'...")
        NiftyPDFGenerator.generate(processed_df, output_pdf)

        logging.info("Distributing PDF reports via email...")
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
