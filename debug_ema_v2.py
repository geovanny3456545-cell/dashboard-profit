import yfinance as yf
import pandas as pd
import numpy as np

def calculate_ema(data, span):
    return data.ewm(span=span, adjust=False).mean()

def check_ticker(symbol):
    ticker = symbol if symbol.endswith('.SA') else f"{symbol}.SA"
    print(f"\n=== Checking {ticker} ===")
    
    for interval_label, interval in [('1W', '1wk'), ('1M', '1mo')]:
        print(f"\nInterval: {interval_label}")
        data = yf.download(ticker, period="10y", interval=interval, progress=False)
        if data.empty:
            print("No data found.")
            continue
            
        # Standardize columns
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [c[0] for c in data.columns]
        
        close = data['Close']
        ema20 = calculate_ema(close, 20)
        
        last_close = close.iloc[-1]
        last_ema = ema20.iloc[-1]
        
        print(f"Latest Close: {last_close:.2f}")
        print(f"Latest EMA 20: {last_ema:.2f}")
        
        # Check if 8.58 appears in the last few EMAs
        recent_emas = ema20.tail(5)
        if any(np.isclose(recent_emas, 8.58, atol=0.1)):
            print("FOUND match near 8.58 in recent EMA history!")
            print(recent_emas)

if __name__ == "__main__":
    check_ticker("NATU3")
    check_ticker("NTCO3")
