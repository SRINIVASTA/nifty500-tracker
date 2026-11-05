import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, date

from src.data_engine import NiftyDataEngine
from src.pdf_generator import NiftyPDFGenerator
from src.email_service import EnterpriseEmailService

st.set_page_config(
    page_title="Nifty 500 Terminal", page_icon="📊", layout="wide"
)

engine = NiftyDataEngine()

if "market_data" not in st.session_state:
    st.session_state.market_data = None
if "last_generated_pdf" not in st.session_state:
    st.session_state.last_generated_pdf = "Nifty500_Filtered_Report.pdf"

st.title("📊 Nifty 500 Market Performance Enterprise Workspace")
st.markdown("Automated ingestion pipeline mapping tracking deltas with interactive absolute price variance analysis dashboards.")

# --- SIDEBAR RUNTIME PANEL ---
st.sidebar.header("⚙️ Pipeline Execution Control")

st.sidebar.subheader("📅 Date Horizon Filters")
start_date = st.sidebar.date_input("Start Date", value=date(2026, 11, 1))
end_date = st.sidebar.date_input("End Date", value=date(2026, 11, 5))

st.sidebar.subheader("💰 Valuation Matrix Range")
price_from = st.sidebar.number_input("Price From (₹)", min_value=0.0, value=0.0, step=50.0)
price_to = st.sidebar.number_input("Price To (₹)", min_value=0.0, value=100000.0, step=50.0)

fetch_trigger = st.sidebar.button("Execute Live Ingestion", type="primary", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.header("📧 Document Delivery Terminal")

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
    if start_date > end_date:
        st.error("❌ Pipeline Aborted: 'Start Date' cannot fall after the chosen 'End Date'.")
    elif price_from > price_to:
        st.error("❌ Pipeline Aborted: 'Price From' threshold cannot exceed 'Price To' threshold.")
    else:
        with st.spinner("Fetching live pricing data from market feeds & evaluating absolute deltas..."):
            try:
                master_list = engine.fetch_master_list()
                processed_df = engine.process_daily_performance(master_list, start_date, end_date)
                
                st.session_state.market_data = processed_df
                st.success(f"Live Ingestion Completed! Active base coverage: {len(processed_df)} securities.")
            except Exception as error:
                st.error(f"Pipeline Execution Aborted: {str(error)}")

# --- VISUAL CONTROL DESK: MASTER WORKSPACE ENTRY ---
if st.session_state.market_data is not None:
    df = st.session_state.market_data.copy()
    is_live_feed = True
    
    yesterday_col = [c for c in df.columns if "Close (" in c]
    active_close_col = yesterday_col[-1] if yesterday_col else None
    
    if active_close_col and not df.empty:
        df = df[(df[active_close_col] >= price_from) & (df[active_close_col] <= price_to)]
else:
    try:
        df = engine.fetch_master_list()
        is_live_feed = False
    except Exception as initialization_error:
        st.error(f"Failed to pre-populate index ledger: {str(initialization_error)}")
        df = pd.DataFrame()
        is_live_feed = False

# Render the Desktop View Grid if data layout is verified
if not df.empty:
    if is_live_feed:
        up_scrip = int((df["Direction"] == "Up").sum())
        down_scrip = int((df["Direction"] == "Down").sum())
        avg_shift = float(df["Price Change"].mean()) if len(df) > 0 else 0.0
        
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric(label="Advancing Markets (🟢)", value=up_scrip)
        kpi2.metric(label="Declining Markets (🔴)", value=down_scrip)
        kpi3.metric(label="Index Price Delta Mean", value=f"₹{avg_shift:+.2f}")
        
        NiftyPDFGenerator.generate(df, st.session_state.last_generated_pdf)
    else:
        st.warning("⚠️ Hub Pipeline Standby: Displaying structural index tracking registry. Live metrics will map below after running execution pipeline.")
    
    tab_grid, tab_analytics = st.tabs(["📋 Master Ledger Workspace", "📈 Cross-Sectional Analytics"])
    
    with tab_grid:
        symbol_col = "NSE Ticker Symbol" if is_live_feed else "Symbol"
        
        search_query = st.text_input("Filter Ledger (Symbol / Company Name)", key="matrix_search_filter")
        filtered_df = df
        if search_query:
            if symbol_col in df.columns and "Company Name" in df.columns:
                filtered_df = df[
                    df[symbol_col].str.contains(search_query, case=False) | 
                    df["Company Name"].str.contains(search_query, case=False)
                ]
            
        if is_live_feed:
            final_columns_view = [symbol_col, "Company Name", active_close_col, "Price Change", "Direction"]
            formatted_df = filtered_df[final_columns_view].copy()
            
            formatted_df = formatted_df.rename(columns={
                active_close_col: "Enddate Close Price",
                "Direction": "up/down"
            })
            
            st.dataframe(
                formatted_df.style.format({
                    "Enddate Close Price": "₹{:,.2f}",
                    "Price Change": "₹{:+.2f}"
                }).map(
                    lambda val: "color: #00875A; font-weight: bold;" if val == "Up" else ("color: #DE350B; font-weight: bold;" if val == "Down" else ""),
                    subset=["up/down"]
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
                    file_name="Nifty500_Filtered_Performance.pdf",
                    mime="application/pdf"
                )
                
    with tab_analytics:
        if is_live_feed:
            if not df.empty:
                col_vis1, col_vis2 = st.columns(2)
                with col_vis1:
                    st.subheader("Market Breadth Allocation")
                    fig_pie = px.pie(df, names="Direction", color="Direction", 
                                     color_discrete_map={"Up": "#00875A", "Down": "#DE350B"}, hole=0.4)
                    st.plotly_chart(fig_pie, use_container_width=True)
                    
                with col_vis2:
                    st.subheader("Top Performers (By Absolute Rupee Change)")
                    sorted_df = df.sort_values(by="Price Change")
                    top_performers = pd.concat([sorted_df.head(5), sorted_df.tail(5)]).drop_duplicates()
                    fig_bar = px.bar(top_performers, x="Price Change", y="NSE Ticker Symbol", orientation="h",
                                     color="Direction", color_discrete_map={"Up": "#00875A", "Down": "#DE350B"})
                    st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("💡 No analytics data available for the selected price thresholds.")
        else:
            st.info("📈 Analytics Engine Offline. Cross-sectional charts will plot here once market streaming data finishes processing.")
else:
    st.info("💡 Ingestion Hub Data Structure Empty or No Securities Match Your Price Filter Settings.")

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
                    subject="Automated Executive Briefing: Absolute Variance Matrix",
                    body=f"Team,\n\nPlease find attached the filtered structural tracking ledger mapping absolute rupee movements.\n\nFilters Applied:\n- Price Range: ₹{price_from:,.2f} to ₹{price_to:,.2f}\n- Target Tracking Interval: {start_date} to {end_date}"
                )
                st.sidebar.success(f"🚀 Filtered PDF Report successfully sent to your secure distribution list!")
            except Exception as email_error:
                st.sidebar.error(f"Transmission Failed: {str(email_error)}")
