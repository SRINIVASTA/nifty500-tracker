import os
from io import BytesIO
import pandas as pd
import requests

def build_local_nifty_matrix():
    # 1. Setup Enterprise Directory Paths
    target_dir = "data"
    target_file = os.path.join(target_dir, "ind_nifty500list.csv")
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"Created directory: '{target_dir}'")

    # 2. Extract Validated Index Array Map from High-Confidence Mirror Pools
    url = "https://niftyindices.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    print("Ingesting structured Nifty 500 index matrix from repository mirror...")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            df = pd.read_csv(BytesIO(response.content), on_bad_lines='skip')
            df.columns = df.columns.str.strip()
            
            required_cols = ["Company Name", "Industry", "Symbol"]
            if all(col in df.columns for col in required_cols):
                df_clean = df[required_cols].sort_values(by="Symbol").reset_index(drop=True)
                
                # 3. Write clean, formatted CSV ledger directly to the data folder
                df_clean.to_csv(target_file, index=False)
                print(f"🚀 Success! Clean dataset saved with {len(df_clean)} assets.")
                print(f"Location: '{target_file}'")
                return
            else:
                print("⚠️ Downloaded layout schema mismatched header structures. Trying fallback...")
        
        # Fallback pool mapping if pathway 1 drops
        fallback_url = "https://githubusercontent.com"
        response = requests.get(fallback_url, timeout=15)
        df = pd.read_csv(BytesIO(response.content), on_bad_lines='skip')
        df.columns = df.columns.str.strip()
        
        if "Symbol" in df.columns:
            df.to_csv(target_file, index=False)
            print(f"🚀 Success via Fallback Channel! Saved {len(df)} assets to '{target_file}'")
            
    except Exception as error:
        print(f"❌ Failed to construct data matrix: {error}")

if __name__ == "__main__":
    build_local_nifty_matrix()
