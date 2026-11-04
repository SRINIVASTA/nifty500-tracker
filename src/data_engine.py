import os
from io import BytesIO
import pandas as pd
import requests
import yfinance as yf

class NiftyDataEngine:
    """Enterprise Data Engine for fetching and parsing Nifty 500 Market Performance data efficiently."""
    
    def __init__(self):
        self.url = "https://niftyindices.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def fetch_master_list(self) -> pd.DataFrame:
        """Retrieves official Nifty 500 components from NSE."""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                df = pd.read_csv(BytesIO(response.content))
                return df.sort_values(by="Symbol").reset_index(drop=True)
            else:
                raise RuntimeError(f"NSE Server returned status code: {response.status_code}")
        except Exception as e:
            raise RuntimeError(f"Failed to fetch Nifty 500 index master: {str(e)}")

    def process_daily_performance(self, df_nifty: pd.DataFrame) -> pd.DataFrame:
        """Downloads window-close pricing metrics using high-speed parallelized batch pools."""
        # Standardise tickers for Yahoo Finance
        df_nifty["YF_Ticker"] = df_nifty["Symbol"].apply(
            lambda x: str(x).replace("&", "%26") + ".NS"
        )
        ticker_list = df_nifty["YF_Ticker"].tolist()

        # Batch download with multi-threading enabled
        market_data = yf.download(
            tickers=" ".join(ticker_list),
            period="5d",
            group_by="ticker",
            threads=True,
            progress=False,
            timeout=15
        )

        if market_data.empty:
            raise ValueError("No data returned from Yahoo Finance. Verify connectivity.")

        results = []
        header_day_before = "Day-Before-Yesterday Close (₹)"
        header_yesterday = "Yesterday Close (₹)"
        dates_captured = False

        # Process each stock by safely extracting from the MultiIndex columns
        for _, row in df_nifty.iterrows():
            symbol = row["Symbol"]
            company_name = row["Company Name"]
            industry = row["Industry"]
            yf_symbol = row["YF_Ticker"]

            try:
                # Standardise column extraction regardless of yfinance multi-index configuration variations
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

        if not results:
            raise ValueError("Data extraction mapping failed due to structure parsing anomalies.")

        return pd.DataFrame(results)
