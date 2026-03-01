import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def test_5m_proxies():
    # Use dates from the user's data: 15/01/2026
    # Note: 5m data is only available for 60 days. 
    # Current date is 2026-03-01.
    # 60 days ago is ~ Jan 1st 2026.
    
    target_date = datetime(2026, 1, 15)
    start_date = target_date
    end_date = target_date + timedelta(days=1)
    
    symbols = ['^BVSP', 'USDBRL=X']
    
    for symbol in symbols:
        print(f"\nTesting {symbol} (5m interval) for {target_date.date()}:")
        try:
            # For 5m data, yf usually requires a very specific range if it's old
            df = yf.download(symbol, start=start_date, end=end_date, interval='5m', progress=False)
            if not df.empty:
                print(f"Success! Found {len(df)} bars.")
                print(df.head(2))
            else:
                print("No data found for this specific date.")
                # Try a more recent date to confirm 5m works at all
                recent_start = datetime.now() - timedelta(days=2)
                recent_end = datetime.now()
                df_recent = yf.download(symbol, start=recent_start, end=recent_end, interval='5m', progress=False)
                if not df_recent.empty:
                    print(f"Verified: 5m works for recent data ({len(df_recent)} bars).")
                else:
                    print("Error: 5m fails even for recent data.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_5m_proxies()
