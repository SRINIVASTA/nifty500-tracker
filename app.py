import streamlit as st
import pandas as pd
import plotly.express as px
import os

from src.data_engine import NiftyDataEngine
from src.pdf_generator import NiftyPDFGenerator
from src.email_service import EnterpriseEmailService

st.set_page_config(
    page_title="Nifty 500 Terminal", page_icon="📊", layout="wide"
)

if "market_data" not in st.session_state:
    st.session_state.market_data = None
if "last_generated_pdf" not in st.session_state:
    st.session_state.last_generated_pdf = "Nifty500_Master_Report.pdf"

st.title("📊 Nifty 500 Market Performance Enterprise Workspace")
st.markdown("Automated ingestion pipeline mapping tracking deltas with interactive cross-sectional analysis dashboards.")

st.sidebar.header("⚙️ Pipeline Execution Control")
fetch_trigger = st.sidebar.button("Execute Live Ingestion", type="primary", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.header("📧 Document Delivery Terminal")
recipient = st.sidebar.text_input("Target Email Address", placeholder="exec@firm.com")

with st.sidebar.expander("🔐 SMTP Relay Security Settings"):
    smtp_host = st.text_input("SMTP Host", value="://gmail.com")
    smtp_port = st.number_input("SMTP Port", value=587)
    auth_email = st.text_input("Auth User Email", placeholder="pipeline@firm.com")
    auth_pass = st.text_input("App Password", type="password")

email_trigger = st.sidebar.button("Dispatch PDF Report", use_container_width=True)

if fetch_trigger:
    with st.spinner("Fetching data from NSE servers & evaluating histories..."):
        try:
            engine = NiftyDataEngine()
            master_list = engine.fetch_master_list()
            processed_df = engine.process_daily_performance(master_list)
            
            st.session_state.market_data = processed_df
            st.success(f"Ingestion completed! Active coverage: {len(processed_df)} / 500 securities.")
            
            NiftyPDFGenerator.generate(processed_df, st.session_state.last_generated_pdf)
        except Exception as error:
            st.error(f"Pipeline Execution Aborted: {str(error)}")

if st.session_state.market_data is not None:
    df = st.session_state.market_data
    
    up_scrip = int((df["Direction"] == "Up").sum())
    down_scrip = int((df["Direction"] == "Down").sum())
    avg_shift = float(df["% Change"].mean())
    
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(label="Advancing Markets (🟢)", value=up_scrip)
    kpi2.metric(label="Declining Markets (🔴)", value=down_scrip)
    kpi3.metric(label="Index Delta Mean", value=f"{avg_shift:+.2f}%")
    
    tab_grid, tab_analytics = st.tabs(["📋 Master Ledger Workspace", "📈 Cross-Sectional Analytics"])
    
    with tab_grid:
        search_query = st.text_input("Filter Ledger (Symbol / Company Name)")
        filtered_df = df
        if search_query:
            filtered_df = df[
                df["NSE Ticker Symbol"].str.contains(search_query, case=False) | 
                df["Company Name"].str.contains(search_query, case=False)
            ]
            
        st.dataframe(
            filtered_df.style.map(
                lambda val: "color: #00875A;" if val == "Up" else ("color: #DE350B;" if val == "Down" else ""),
                subset=["Direction"]
            ),
            use_container_width=True,
            height=450
        )
        
        if os.path.exists(st.session_state.last_generated_pdf):
            with open(st.session_state.last_generated_pdf, "rb") as file_bytes:
                st.download_button(
                    label="📥 Download Executable PDF Ledger",
                    data=file_bytes,
                    file_name="Nifty500_Market_Performance.pdf",
                    mime="application/pdf"
                )
                
    with tab_analytics:
        col_vis1, col_vis2 = st.columns(2)
        with col_vis1:
            st.subheader("Market Breadth Allocation")
            fig_pie = px.pie(df, names="Direction", color="Direction", 
                             color_discrete_map={"Up": "#00875A", "Down": "#DE350B"}, hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_vis2:
            st.subheader("Top Performers (Extreme Ends)")
            sorted_df = df.sort_values(by="% Change")
            top_performers = pd.concat([sorted_df.head(5), sorted_df.tail(5)])
            fig_bar = px.bar(top_performers, x="% Change", y="NSE Ticker Symbol", orientation="h",
                             color="Direction", color_discrete_map={"Up": "#00875A", "Down": "#DE350B"})
            st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("💡 Hub Pipeline Offline. Click 'Execute Live Ingestion' in the sidebar panel to synchronize market state data.")

if email_trigger:
    if st.session_state.market_data is None:
        st.sidebar.error("Data missing! Extract active parameters first.")
    elif not recipient or not auth_email or not auth_pass:
        st.sidebar.error("Required Cryptographic Authentication details missing!")
    else:
        with st.spinner("Establishing secure TLS connection, routing ledger..."):
            try:
                EnterpriseEmailService.send_report(
                    recipient_email=recipient,
                    attachment_path=st.session_state.last_generated_pdf,
                    smtp_server=smtp_host,
                    smtp_port=smtp_port,
                    sender_email=auth_email,
                    sender_password=auth_pass
                )
                st.sidebar.success(f"Report dispatched to: '{recipient}'")
            except Exception as email_error:
                st.sidebar.error(f"Transmission Failed: {str(email_error)}")
