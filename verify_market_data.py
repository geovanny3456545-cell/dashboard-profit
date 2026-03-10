import pandas as pd
import sys
import os

# Set CWD to ensure imports work
sys.path.append(os.getcwd())

from utils.data_loader import fetch_real_ohlc

def verify_market_data():
    test_symbols = ['PETR4', 'VALE3']
    periods = ['1W', '1M']
    
    print("Testing Real Market Data Fetching (FIXED SCRIPT)...")
    
    for symbol in test_symbols:
        for period in periods:
            print(f"\nFetching {symbol} ({period})...")
            df = fetch_real_ohlc(symbol, period)
            if df.empty:
                print(f"FAILED: No data for {symbol}")
            else:
                print(f"SUCCESS: Found {len(df)} candles.")
                print(f"Available Columns: {df.columns.tolist()}")
                # Access by name, ignoring case or exact match if needed
                cols = [c for c in ['Date', 'Open', 'High', 'Low', 'Close'] if c in df.columns]
                print(df[cols].tail(2))

if __name__ == "__main__":
    verify_market_data()
