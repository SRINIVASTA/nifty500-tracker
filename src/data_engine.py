import os
from io import BytesIO
import pandas as pd
import requests
import yfinance as yf
import streamlit as st
from datetime import datetime

class NiftyDataEngine:
    """Enterprise Data Engine for fetching and parsing Nifty 500 Market Performance data efficiently."""
    
    def __init__(self):
        self.local_path = os.path.join("data", "ind_nifty500list.csv")
        self.url = "https://nsearchives.nseindia.com/content/indices/ind_nifty500list.csv"
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
                st.warning(f"⚠️ Local repository file read anomaly: {local_err}. Falling back to mirrors...")

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
                    raise RuntimeError("Server returned HTML firewall block page.")
                df = pd.read_csv(BytesIO(response.content), on_bad_lines='skip')
                df.columns = df.columns.str.strip()
                if 'Symbol' in df.columns:
                    return df.sort_values(by="Symbol").reset_index(drop=True)
            raise RuntimeError(f"Server response error: {response.status_code}")
            
        except Exception as e:
            raise RuntimeError(f"All ingest pathways exhausted: {str(e)}")

    def process_daily_performance(self, df_nifty: pd.DataFrame, start_date=None, end_date=None) -> pd.DataFrame:
        """Downloads exact window closing prices handling user-defined start and end dates dynamically."""
        if df_nifty.empty or "Symbol" not in df_nifty.columns:
            return pd.DataFrame()

        # Fallbacks to yesterday/today if UI arguments are missing
        if start_date is None:
            start_date = (datetime.today() - pd.Timedelta(days=2)).date()
        if end_date is None:
            end_date = datetime.today().date()

        # Add 1 day to end_date because yfinance historical downloads exclude the last boundary day
        yf_start = start_date.strftime("%Y-%m-%d")
        yf_end = (end_date + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

        df_nifty["YF_Ticker"] = df_nifty["Symbol"].apply(
            lambda x: str(x).replace("&", "%26").strip() + ".NS"
        )
        ticker_list = df_nifty["YF_Ticker"].tolist()

        # Fetch explicitly within the custom user date ranges
        market_data = yf.download(
            tickers=" ".join(ticker_list),
            start=yf_start,
            end=yf_end,
            group_by="ticker",
            threads=True,
            progress=False,
            timeout=20
        )

        if market_data.empty:
            raise ValueError("No pricing data returned from Yahoo Finance for selected dates.")

        results = []
        
        # Enforce header labels dynamically matching your chosen operational dates
        str_start_date = start_date.strftime("%Y-%m-%d")
        str_end_date = end_date.strftime("%Y-%m-%d")
        
        header_start = f"Close ({str_start_date}) (₹)"
        header_end = f"Close ({str_end_date}) (₹)"

        for _, row in df_nifty.iterrows():
            symbol = row["Symbol"]
            company_name = row.get("Company Name", symbol)
            industry = row.get("Industry", "N/A")
            yf_symbol = row["YF_Ticker"]

            try:
                # Isolate target ticker frame array data
                if yf_symbol in market_data.columns.get_level_values(0):
                    ticker_history = market_data[yf_symbol].dropna(subset=["Close"])
                elif "Close" in market_data.columns.get_level_values(0) and yf_symbol in market_data.columns.get_level_values(1):
                    ticker_history = market_data.xs(yf_symbol, axis=1, level=1).dropna(subset=["Close"])
                else:
                    continue

                if not ticker_history.empty:
                    # Dynamically look for the row corresponding exactly to your date options
                    history_dates = ticker_history.index.strftime("%Y-%m-%d")
                    
                    if str_start_date in history_dates and str_end_date in history_dates:
                        start_close = float(ticker_history.loc[str_start_date, "Close"])
                        end_close = float(ticker_history.loc[str_end_date, "Close"])
                    else:
                        # Fallback to closest available positional data points if market holidays are chosen
                        if len(ticker_history) >= 2:
                            start_close = float(ticker_history["Close"].iloc[0])
                            end_close = float(ticker_history["Close"].iloc[-1])
                        else:
                            continue

                    if start_close == 0 or pd.isna(start_close) or pd.isna(end_close):
                        continue

                    # Evaluate metrics using actual end data points 
                    price_change = end_close - start_close
                    pct_change = (price_change / start_close) * 100
                    direction = "Up" if pct_change >= 0 else "Down"

                    results.append({
                        "NSE Ticker Symbol": symbol,
                        "Company Name": company_name,
                        "Industry": industry,
                        header_start: round(start_close, 2),
                        header_end: round(end_close, 2),
                        "% Change": round(pct_change, 2),
                        "Direction": direction,
                        # Map To-Date close explicitly into the columns requested by your PDF
                        "Latest closing price (₹)": round(end_close, 2),
                        "Price Change (+/-)": round(price_change, 2)
                    })
            except Exception:
                continue

        return pd.DataFrame(results)
