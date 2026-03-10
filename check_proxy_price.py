import yfinance as yf
import datetime
import pandas as pd

def check_proxy_price():
    # Trade date from sample: 15/01/2026
    trade_dt = datetime.datetime(2026, 1, 15, 9, 13)
    start = trade_dt - datetime.timedelta(hours=1)
    end = trade_dt + datetime.timedelta(hours=1)
    
    symbol = "^BVSP"
    df = yf.download(symbol, start=start, end=end, interval='5m', progress=False)
    
    if not df.empty:
        print(f"Proxy ({symbol}) prices at {trade_dt}:")
        print(df['Close'].iloc[0])
    else:
        print(f"No 5m data for {symbol} at {trade_dt}")
        # Try daily
        df_d = yf.download(symbol, start=trade_dt - datetime.timedelta(days=5), end=trade_dt + datetime.timedelta(days=5))
        if not df_d.empty:
             print(f"Daily ({symbol}) prices around {trade_dt}:")
             print(df_d['Close'].tail())

if __name__ == "__main__":
    check_proxy_price()
