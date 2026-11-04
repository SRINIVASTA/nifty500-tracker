import os
from io import BytesIO
import pandas as pd
import requests
import yfinance as yf
import streamlit as st

class NiftyDataEngine:
    """Enterprise Data Engine for fetching and parsing Nifty 500 Market Performance data efficiently."""
    
    def __init__(self):
        # Local relative track layout
        self.local_path = os.path.join("data", "ind_nifty500list.csv")
        # Live web tracking fallback slug
        self.url = "https://niftyindices.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

    @st.cache_data(ttl=3600)
    def fetch_master_list(_self) -> pd.DataFrame:
        """Retrieves Nifty 500 components, prioritizing high-speed local data files first."""
        # PATHWAY 1: High-Speed Enterprise Local Repository Reading
        if os.path.exists(_self.local_path):
            try:
                df = pd.read_csv(_self.local_path, on_bad_lines='skip')
                df.columns = df.columns.str.strip()
                if 'Symbol' in df.columns:
                    return df.sort_values(by="Symbol").reset_index(drop=True)
            except Exception as local_err:
                st.warning(f"⚠️ Local repository file read anomaly: {local_err}. Falling back to web streams...")

        # PATHWAY 2: Live Network Server Stream Fallback
        try:
            response = requests.get(_self.url, headers=_self.headers, timeout=10)
            if response.status_code == 200:
                df = pd.read_csv(BytesIO(response.content), on_bad_lines='skip')
                df.columns = df.columns.str.strip()
                if 'Symbol' in df.columns:
                    return df.sort_values(by="Symbol").reset_index(drop=True)
            raise RuntimeError(f"Server response logic error: {response.status_code}")
            
        except Exception as e:
            # PATHWAY 3: Secure Public Repository Mirror Check
            fallback_url = "https://githubusercontent.com"
            try:
                response = requests.get(fallback_url, timeout=10)
                df = pd.read_csv(BytesIO(response.content), on_bad_lines='skip')
                df.columns = df.columns.str.strip()
                return df.sort_values(by="Symbol").reset_index(drop=True)
            except Exception:
                raise RuntimeError(f"All structural ingest pathways exhausted. Technical source exception: {str(e)}")

    def process_daily_performance(self, df_nifty: pd.DataFrame) -> pd.DataFrame:
        """Downloads window-close pricing metrics using high-speed parallelized batch pools."""
        if df_nifty.empty or "Symbol" not in df_nifty.columns:
            return pd.DataFrame()

        df_nifty["YF_Ticker"] = df_nifty["Symbol"].apply(
            lambda x: str(x).replace("&", "%26").strip() + ".NS"
        )
        ticker_list = df_nifty["YF_Ticker"].tolist()

        # High-concurrency array retrieval wrapper
        market_data = yf.download(
            tickers=" ".join(ticker_list),
            period="5d",
            group_by="ticker",
            threads=True,
            progress=False,
            timeout=20
        )

        if market_data.empty:
            raise ValueError("No data returned from Yahoo Finance. Verify connectivity.")

        results = []
        header_day_before = "Day-Before-Yesterday Close (₹)"
        header_yesterday = "Yesterday Close (₹)"
        dates_captured = False

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

                if len(ticker_history) >= 2:
                    if not dates_captured:
                        db_date = ticker_history.index[-2].strftime("%Y-%m-%d")
                        y_date = ticker_history.index[-1].strftime("%Y-%m-%d")
                        header_day_before = f"Close ({db_date}) (₹)"
                        header_yesterday = f"Close ({y_date}) (₹)"
                        dates_captured = True

                    yesterday_close = float(ticker_history["Close"].iloc[-1])
                    day_before_close = float(ticker_history["Close"].iloc[-2])

                    if day_before_close == 0:
                        continue

                    pct_change = ((yesterday_close - day_before_close) / day_before_close) * 100
                    direction = "Up" if pct_change >= 0 else "Down"

                    results.append({
                        "NSE Ticker Symbol": symbol,
                        "Company Name": company_name,
                        "Industry": industry,
                        header_day_before: round(day_before_close, 2),
                        header_yesterday: round(yesterday_close, 2),
                        "% Change": round(pct_change, 2),
                        "Direction": direction
                    })
            except Exception:
                continue

        return pd.DataFrame(results)
