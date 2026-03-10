import yfinance as yf
import pandas as pd
import numpy as np

def test_variants(symbol):
    ticker = f"{symbol}.SA" if not symbol.endswith('.SA') else symbol
    print(f"\n--- Testing Variants for {ticker} (1W) ---")
    
    # Try different combinations
    for adj in [False, True]:
        for auto in [False, True]:
            data = yf.download(ticker, period="5y", interval="1wk", auto_adjust=auto, progress=False)
            if data.empty: continue
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = [c[0] for c in data.columns]
            
            # Clean
            data['Close'] = data['Close'].replace(0, np.nan).ffill().bfill()
            
            # EMA
            data['EMA20'] = data['Close'].ewm(span=20, adjust=adj).mean()
            
            val = data['EMA20'].iloc[-1]
            print(f"adjust={adj}, auto_adjust={auto} => EMA 20: {val:.4f} (Close: {data['Close'].iloc[-1]:.2f})")
            if abs(val - 8.58) < 0.1:
                print(">>> MATCH FOUND! <<<")

if __name__ == "__main__":
    test_variants("NATU3")
