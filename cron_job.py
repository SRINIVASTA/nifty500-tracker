#!/usr/bin/env python3
import os
import logging
from datetime import date, timedelta

# Bind project engines
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

def run_unattended_pipeline():
    logging.info("🚀 Initializing Streamlit-Linked Market Matrix Pipeline...")
    
    # Define tracking dates (Trailing 3 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=3)
    
    # Locate configuration variables directly from your secrets file layout
    secrets_path = os.path.join(".streamlit", "secrets.toml")
    if not os.path.exists(secrets_path):
        logging.error(f"❌ Aborted: Streamlit secrets ledger not found at target: {secrets_path}")
        return

    try:
        import toml
        secrets = toml.load(secrets_path)
        
        # Read directly into active variables from your file structure
        sender_email = secrets["gmail"]["username"]
        app_password = secrets["gmail"]["app_password"]
        recipient_list = secrets["gmail"]["to_email"]
        logging.info("✓ Credentials successfully mapped from Streamlit secrets file.")
    except Exception as err:
        logging.error(f"❌ Failed to parse secrets.toml file structures: {err}")
        return

    # Check that none of the read fields are blank or missing
    if not (sender_email and app_password and recipient_list):
        logging.error("❌ Aborted: One or more fields under [gmail] are completely empty inside secrets.toml.")
        return

    output_pdf = "Nifty500_Automated_Briefing.pdf"

    try:
        engine = NiftyDataEngine()
        master_list = engine.fetch_master_list()
        
        logging.info(f"Evaluating absolute price changes from {start_date} to {end_date}...")
        processed_df = engine.process_daily_performance(master_list, start_date, end_date)
        
        if processed_df.empty:
            logging.error("❌ Data Engine returned an empty matrix payload.")
            return

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

if __name__ == "__main__":
    run_unattended_pipeline()
