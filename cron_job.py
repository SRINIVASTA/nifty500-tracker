#!/usr/bin/env python3
import os
import sys
import logging
from datetime import date, timedelta
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.data_engine import NiftyDataEngine
from src.pdf_generator import NiftyPDFGenerator
from src.email_service import EnterpriseEmailService

SECRETS_PATH = ROOT_DIR / ".streamlit" / "secrets.toml"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("pipeline_automation.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

def _load_smtp_credentials() -> tuple[str, str, str]:
    """Load credentials from GitHub Secrets first, then fallback to local .streamlit/secrets.toml."""
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

def _get_weekly_dates() -> tuple[date, date]:
    """Anchor start_date to Monday of the current week and advance end_date daily through Friday."""
    end_date = date.today()
    start_date = end_date - timedelta(days=end_date.weekday())
    if end_date.weekday() == 0:
        start_date = end_date - timedelta(days=7)
    return start_date, end_date

def _filter_by_price(df, price_from: float = 100.0, price_to: float = 1000.0):
    """Keep only stocks priced between ₹100 and ₹1,000."""
    candidate_cols = [
        "Close", "Current Price", "LTP", "End Price", "Latest Price",
        "close", "current_price", "ltp", "end_price", "Price", "price"
    ]
    price_col = next((col for col in candidate_cols if col in df.columns), None)

    if price_col is None:
        numeric_cols = [
            c for c in df.select_dtypes(include="number").columns
            if "pct" not in c.lower() and "%" not in c and "change" not in c.lower() and "delta" not in c.lower()
        ]
        price_col = numeric_cols[-1] if numeric_cols else None

    if price_col is None:
        logging.warning(f"⚠️ Price column not identified from {list(df.columns)}. Skipping price filter.")
        return df

    logging.info(f"Applying price filter on '{price_col}': ₹{price_from:.2f} to ₹{price_to:.2f}")
    return df[(df[price_col] >= price_from) & (df[price_col] <= price_to)].copy()

def run_unattended_pipeline():
    logging.info("🚀 Initializing Nifty 500 Market Matrix Pipeline...")

    start_date, end_date = _get_weekly_dates()
    price_from, price_to = 100.0, 1000.0

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

        filtered_df = _filter_by_price(processed_df, price_from, price_to)
        logging.info(f"Filtered to {len(filtered_df)} stocks priced between ₹{price_from:.0f} and ₹{price_to:.0f}.")

        if filtered_df.empty:
            logging.error(f"❌ No stocks found in price range ₹{price_from:.0f} to ₹{price_to:.0f}.")
            sys.exit(1)

        logging.info(f"Compiling PDF report into: '{output_pdf}'...")
        NiftyPDFGenerator.generate(filtered_df, output_pdf)

        logging.info("Distributing PDF reports via email...")
        total_sent = EnterpriseEmailService.send_report(
            recipient_string=recipient_list,
            attachment_path=output_pdf,
            sender_email=sender_email,
            app_password=app_password,
            subject=f"Automated Matrix Briefing: Nifty 500 [{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}]",
            body=(
                f"Team,\n\n"
                f"Please find attached the automated portrait tracking ledger mapping absolute index delta shifts.\n\n"
                f"Execution Summary Metrics:\n"
                f"- Window Interval Checked: {start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}\n"
                f"- Valuation Matrix Range: ₹{price_from:,.2f} to ₹{price_to:,.2f}\n"
                f"- Tracked Asset Registry Count: {len(filtered_df)} Filtered Listings\n\n"
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
