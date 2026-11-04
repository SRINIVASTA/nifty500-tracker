import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta

from src.data_engine import NiftyDataEngine
from src.pdf_generator import NiftyPDFGenerator
from src.email_service import EnterpriseEmailService

st.set_page_config(
    page_title="Nifty 500 Terminal", page_icon="📊", layout="wide"
)

# Instantiate the engine to handle data state transitions
engine = NiftyDataEngine()

if "market_data" not in st.session_state:
    st.session_state.market_data = None
if "last_generated_pdf" not in st.session_state:
    st.session_state.last_generated_pdf = "Nifty500_Master_Report.pdf"

st.title("📊 Nifty 500 Market Performance Enterprise Workspace")
st.markdown("Automated ingestion pipeline mapping tracking deltas with interactive cross-sectional analysis dashboards.")

# --- SIDEBAR RUNTIME PANEL ---
st.sidebar.header("⚙️ Pipeline Execution Control")

# Date Selection Panel
col_d1, col_d2 = st.sidebar.columns(2)
with col_d1:
    start_date = st.date_input("Start Date", datetime.today() - timedelta(days=1))
with col_d2:
    end_date = st.date_input("End Date", datetime.today())

# Price Ingestion Filter Panel
col_p1, col_p2 = st.sidebar.columns(2)
with col_p1:
    price_from = st.number_input("Price From (₹)", min_value=0.0, value=100.0, step=50.0)
with col_p2:
    price_to = st.number_input("Price To (₹)", min_value=0.0, value=1000.0, step=50.0)

fetch_trigger = st.sidebar.button("Execute Live Ingestion", type="primary", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.header("📧 Document Delivery Terminal")

# Fetch credentials and default recipients silently from secrets
try:
    email_sender = st.secrets["gmail"]["username"]
    app_password = st.secrets["gmail"]["app_password"]
    recipient_input = st.secrets["gmail"]["to_email"]
    secrets_loaded = True
except KeyError:
    email_sender = ""
    app_password = ""
    recipient_input = ""
    secrets_loaded = False

if not secrets_loaded:
    st.sidebar.error("⚠️ Credentials missing! Configure [gmail] entries in Streamlit Secrets.")

email_trigger = st.sidebar.button("Dispatch PDF Report", use_container_width=True, disabled=not secrets_loaded)

# --- INGESTION CONTROLLER ENGINE ---
if fetch_trigger:
    with st.spinner("Fetching live pricing data from market feeds & evaluating delta trends..."):
        try:
            # 1. Fetch raw matrix data from engine
            master_list = engine.fetch_master_list()
            processed_df = engine.process_daily_performance(master_list)
            
            # 2. Locate Trade Date column setup
            date_col_candidates = ["Trade Date", "Date", "trade_date", "date"]
            found_date_col = None
            for col in processed_df.columns:
                if col in date_col_candidates or "date" in col.lower():
                    found_date_col = col
                    break
            
            # 3. Explicitly extract the closing price on the "To Date" (End Date)
            close_col_candidates = ["Current Close", "Close", "Latest closing price (₹)", "Closing Price"]
            found_close_col = None
            for col in processed_df.columns:
                if col in close_col_candidates or "close" in col.lower() or "price" in col.lower():
                    found_close_col = col
                    break

            if found_date_col and found_close_col:
                processed_df[found_date_col] = pd.to_datetime(processed_df[found_date_col]).dt.date
                
                # Filter down the master frame data strictly to the End Date rows 
                # This guarantees that the calculated closing values are from the "To Date" only
                end_date_df = processed_df[processed_df[found_date_col] == end_date].copy()
                end_date_df["Latest closing price (₹)"] = pd.to_numeric(end_date_df[found_close_col], errors='coerce')
                processed_df = end_date_df
            else:
                if found_close_col:
                    processed_df["Latest closing price (₹)"] = pd.to_numeric(processed_df[found_close_col], errors='coerce')
                else:
                    processed_df["Latest closing price (₹)"] = 0.0

            # 4. Harmonize "Price Change (+/-)" metrics
            if "Price Change (+/-)" not in processed_df.columns:
                if "Price Change" in processed_df.columns:
                    processed_df["Price Change (+/-)"] = processed_df["Price Change"]
                elif "% Change" in processed_df.columns:
                    processed_df["Price Change (+/-)"] = processed_df["% Change"]
                else:
                    processed_df["Price Change (+/-)"] = 0.0

            # 5. Apply Price Range Filter using End Date values
            processed_df = processed_df.dropna(subset=["Latest closing price (₹)"])
            processed_df = processed_df[
                (processed_df["Latest closing price (₹)"] >= price_from) & 
                (processed_df["Latest closing price (₹)"] <= price_to)
            ]

            st.session_state.market_data = processed_df
            st.success(f"Ingestion Finished! Extracted {len(processed_df)} records matching price conditions strictly on: {end_date}.")
            
            # 6. Build PDF with the 5 explicit requested fields
            pdf_cols = ["NSE Ticker Symbol", "Company Name", "Latest closing price (₹)", "Direction", "Price Change (+/-)"]
            
            for target_col in pdf_cols:
                if target_col not in processed_df.columns:
                    if target_col == "NSE Ticker Symbol" and "Symbol" in processed_df.columns:
                        processed_df["NSE Ticker Symbol"] = processed_df["Symbol"]
                    else:
                        processed_df[target_col] = "N/A"
                    
            pdf_export_df = processed_df[pdf_cols]
            NiftyPDFGenerator.generate(pdf_export_df, st.session_state.last_generated_pdf)
            
        except Exception as error:
            st.error(f"Pipeline Execution Aborted: {str(error)}")
# --- VISUAL CONTROL DESK: MASTER WORKSPACE ENTRY ---
if st.session_state.market_data is not None:
    filtered_df = st.session_state.market_data
    is_live_feed = True
else:
    try:
        filtered_df = engine.fetch_master_list()
        is_live_feed = False
    except Exception as initialization_error:
        st.error(f"Failed to pre-populate index ledger: {str(initialization_error)}")
        filtered_df = pd.DataFrame()
        is_live_feed = False

# Render the Desktop View Grid if data layout is verified
if not filtered_df.empty:
    if is_live_feed:
        up_scrip = int((filtered_df["Direction"] == "Up").sum())
        down_scrip = int((filtered_df["Direction"] == "Down").sum())
        
        target_delta_col = "Price Change (+/-)" if "Price Change (+/-)" in filtered_df.columns else "Price Change"
        avg_shift = float(filtered_df[target_delta_col].mean()) if target_delta_col in filtered_df.columns and not filtered_df.empty else 0.0
        
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric(label="Advancing Markets (🟢)", value=up_scrip)
        kpi2.metric(label="Declining Markets (🔴)", value=down_scrip)
        kpi3.metric(label="Index Delta Mean Change", value=f"{avg_shift:+.2f}")
    else:
        st.warning("⚠️ Hub Pipeline Standby: Displaying structural index tracking registry. Live metrics will map below after running execution pipeline.")
    
    tab_grid, tab_analytics = st.tabs(["📋 Master Ledger Workspace", "📈 Cross-Sectional Analytics"])
    
    with tab_grid:
        symbol_col = "NSE Ticker Symbol" if is_live_feed else "Symbol"
        
        search_query = st.text_input("Filter Ledger (Symbol / Company Name)", key="matrix_search_filter")
        if search_query:
            if symbol_col in filtered_df.columns and "Company Name" in filtered_df.columns:
                filtered_df = filtered_df[
                    filtered_df[symbol_col].str.contains(search_query, case=False) | 
                    filtered_df["Company Name"].str.contains(search_query, case=False)
                ]
            
        if is_live_feed:
            formatted_df = filtered_df.copy()
            for col in formatted_df.columns:
                if "Close" in col or "price" in col.lower() or "Price Change" in col:
                    try:
                        formatted_df[col] = formatted_df[col].apply(lambda x: f"₹{x:,.2f}" if isinstance(x, (int, float)) else x)
                    except Exception:
                        pass
                    
            st.dataframe(
                formatted_df.style.map(
                    lambda val: "color: #00875A; font-weight: bold;" if val == "Up" else ("color: #DE350B; font-weight: bold;" if val == "Down" else ""),
                    subset=["Direction"]
                ),
                use_container_width=True,
                height=500
            )
        else:
            st.dataframe(filtered_df[[symbol_col, "Company Name", "Industry"]], use_container_width=True, height=500)
        
        if is_live_feed and os.path.exists(st.session_state.last_generated_pdf):
            with open(st.session_state.last_generated_pdf, "rb") as file_bytes:
                st.download_button(
                    label="📥 Download Executable PDF Ledger",
                    data=file_bytes,
                    file_name="Nifty500_Market_Performance.pdf",
                    mime="application/pdf"
                )
                
    with tab_analytics:
        if is_live_feed:
            if not filtered_df.empty:
                col_vis1, col_vis2 = st.columns(2)
                with col_vis1:
                    st.subheader("Market Breadth Allocation")
                    fig_pie = px.pie(filtered_df, names="Direction", color="Direction", 
                                     color_discrete_map={"Up": "#00875A", "Down": "#DE350B"}, hole=0.4)
                    st.plotly_chart(fig_pie, use_container_width=True)
                    
                with col_vis2:
                    st.subheader("Top Performers (Extreme Ends)")
                    target_sort = "Price Change (+/-)" if "Price Change (+/-)" in filtered_df.columns else filtered_df.columns[-1]
                    sorted_df = filtered_df.sort_values(by=target_sort)
                    top_performers = pd.concat([sorted_df.head(5), sorted_df.tail(5)]).drop_duplicates()
                    fig_bar = px.bar(top_performers, x=target_sort, y="NSE Ticker Symbol", orientation="h",
                                     color="Direction", color_discrete_map={"Up": "#00875A", "Down": "#DE350B"})
                    st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No data matches the selected price scope to display charts.")
        else:
            st.info("📈 Analytics Engine Offline. Cross-sectional charts will plot here once market streaming data finishes processing.")
else:
    st.info("💡 Ingestion Hub Data Structure Empty. Please click 'Execute Live Ingestion' to build market state parameters manually.")

# --- SECURE AUTOMATED EMAIL DISPATCH SYSTEM ---
if email_trigger:
    if st.session_state.market_data is None:
        st.sidebar.error("❌ Data missing! Execute live ingestion first to compile the report data.")
    else:
        with st.spinner("Connecting to secure relays and distributing PDF reports..."):
            try:
                count = EnterpriseEmailService.send_report(
                    recipient_string=recipient_input,
                    attachment_path=st.session_state.last_generated_pdf,
                    sender_email=email_sender,
                    app_password=app_password,
                    subject="Automated Executive Briefing: Nifty 500 Market Matrix",
                    body="Team,\n\nPlease find attached the structured tracking ledger mapping the latest index deltas."
                )
                st.sidebar.success(f"🚀 PDF Report successfully sent to your secure distribution list!")
            except Exception as email_error:
                st.sidebar.error(f"Transmission Failed: {str(email_error)}")
