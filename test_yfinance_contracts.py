import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def test_contract_data():
    # User's data has WING26 on 15/01/2026
    start_date = datetime(2026, 1, 15)
    end_date = datetime(2026, 1, 16)
    
    # Try different formats found in research
    tickers = ['WING26.SA', 'WINJ26.SA', 'WDOH26.SA', 'WING6.SA', 'WDOH6.SA']
    
    for ticker in tickers:
        print(f"\nTesting {ticker} (5m interval) for {start_date.date()}:")
        try:
            df = yf.download(ticker, start=start_date, end=end_date, interval='5m', progress=False)
            if not df.empty:
                print(f"Success! Found {len(df)} bars.")
                print(df.head(2))
            else:
                print("No data found for this contract.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_contract_data()
