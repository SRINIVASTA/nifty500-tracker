import os
from io import BytesIO
import pandas as pd
import requests
import yfinance as yf
import streamlit as st
from datetime import date, timedelta

class NiftyDataEngine:
    """Enterprise Data Engine for fetching and parsing Nifty 500 Market Performance data efficiently."""
    
    def __init__(self):
        self.local_path = os.path.join("data", "ind_nifty500list.csv")
        self.url = "https://nseindia.com"
        self.mirror_url = "https://githubusercontent.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }

    @st.cache_data(ttl=3600)
    def fetch_master_list(_self) -> pd.DataFrame:
        """Retrieves Nifty 500 components, prioritizing high-speed local files, fallback mirrors, and live network arrays."""
        if os.path.exists(_self.local_path):
            try:
                df = pd.read_csv(_self.local_path, on_bad_lines='skip')
                df.columns = df.columns.str.strip()
                if 'Symbol' in df.columns:
                    return df.sort_values(by="Symbol").reset_index(drop=True)
            except Exception as local_err:
                st.warning(f"⚠️ Local repository file read anomaly: {local_err}. Falling back to high-availability network streams...")

        try:
            response = requests.get(_self.mirror_url, timeout=10)
            if response.status_code == 200 and not response.text.strip().startswith("<!DOCTYPE"):
                df = pd.read_csv(BytesIO(response.content), on_bad_lines='skip')
                df.columns = df.columns.str.strip()
                if 'Symbol' in df.columns:
                    try:
                        os.makedirs(os.path.dirname(_self.local_path), exist_ok=True)
                        df.to_csv(_self.local_path, index=False)
                    except Exception:
                        pass
                    return df.sort_values(by="Symbol").reset_index(drop=True)
        except Exception:
            pass

        try:
            response = requests.get(_self.url, headers=_self.headers, timeout=10)
            if response.status_code == 200:
                if response.text.strip().startswith("<!DOCTYPE") or "html" in response.text.lower():
                    raise RuntimeError("Server returned HTML firewall block page instead of structured data matrix.")
                df = pd.read_csv(BytesIO(response.content), on_bad_lines='skip')
                df.columns = df.columns.str.strip()
                if 'Symbol' in df.columns:
                    return df.sort_values(by="Symbol").reset_index(drop=True)
            raise RuntimeError(f"Server response logic error: {response.status_code}")
            
        except Exception as e:
            raise RuntimeError(f"All structural ingest pathways exhausted. Technical source exception: {str(e)}")

    def process_daily_performance(self, df_nifty: pd.DataFrame, start_dt: date, end_dt: date) -> pd.DataFrame:
        """Downloads window pricing metrics across explicit historical target date ranges."""
        if df_nifty.empty or "Symbol" not in df_nifty.columns:
            return pd.DataFrame()

        df_nifty["YF_Ticker"] = df_nifty["Symbol"].apply(
            lambda x: str(x).replace("&", "%26").strip() + ".NS"
        )
        ticker_list = df_nifty["YF_Ticker"].tolist()

        padded_start = start_dt - timedelta(days=5)
        padded_end = end_dt + timedelta(days=5)

        market_data = yf.download(
            tickers=" ".join(ticker_list),
            start=padded_start.strftime("%Y-%m-%d"),
            end=padded_end.strftime("%Y-%m-%d"),
            group_by="ticker",
            threads=True,
            progress=False,
            timeout=25
        )

        if market_data.empty:
            raise ValueError("No data returned from Yahoo Finance. Verify active internet connection and dates.")

        results = []
        dates_captured = False
        header_start_date = "Startdate Close (₹)"
        header_end_date = "Enddate Close Price"

        for _, row in df_nifty.iterrows():
            symbol = row["Symbol"]
            company_name = row.get("Company Name", symbol)
            industry = row.get("Industry", "N/A")
            yf_symbol = row["YF_Ticker"]

            try:
                if yf_symbol in market_data.columns.get_level_values(0):
                    ticker_history = market_data[yf_symbol].dropna(subset=["Close"])
                elif "Close" in market_data.columns.get_level_values(0) and yf_symbol in market_data.columns.get_level_values(1):
                    ticker_history = market_data.xs(yf_symbol, axis=1, level=1).dropna(subset=["Close"])
                else:
                    continue

                if ticker_history.empty:
                    continue

                range_history = ticker_history.loc[start_dt.strftime("%Y-%m-%d"):end_dt.strftime("%Y-%m-%d")]
                
                if range_history.empty:
                    before_range = ticker_history.loc[:end_dt.strftime("%Y-%m-%d")]
                    if before_range.empty:
                        continue
                    range_history = before_range.tail(2)

                if len(range_history) >= 1:
                    start_close = float(range_history["Close"].iloc[0])
                    end_close = float(range_history["Close"].iloc[-1])

                    if not dates_captured:
                        actual_start_str = range_history.index[0].strftime("%Y-%m-%d")
                        actual_end_str = range_history.index[-1].strftime("%Y-%m-%d")
                        header_start_date = f"Close ({actual_start_str}) (₹)"
                        header_end_date = f"Close ({actual_end_str}) (₹)"
                        dates_captured = True

                    if start_close == 0:
                        continue

                    # Calculate absolute price difference delta instead of percentage return
                    absolute_price_change = end_close - start_close
                    direction = "Up" if absolute_price_change >= 0 else "Down"

                    results.append({
                        "NSE Ticker Symbol": symbol,
                        "Company Name": company_name,
                        "Industry": industry,
                        header_start_date: round(start_close, 2),
                        header_end_date: round(end_close, 2),
                        "Price Change": round(absolute_price_change, 2),
                        "Direction": direction
                    })
            except Exception:
                continue

        return pd.DataFrame(results)
