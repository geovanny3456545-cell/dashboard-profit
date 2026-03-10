import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def test_futures():
    symbols = ['WING26.SA', 'WIN=F', 'WDOH26.SA', 'WDO=F', '^BVSP', 'USDBRL=X']
    end_date = datetime(2026, 3, 1)
    start_date = end_date - timedelta(days=7)
    
    for symbol in symbols:
        print(f"\nTesting {symbol} (1h interval):")
        try:
            df = yf.download(symbol, start=start_date, end=end_date, interval='1h', progress=False)
            if not df.empty:
                print(f"Success! Found {len(df)} bars.")
                print(df.head(2))
            else:
                print("No data found.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_futures()
