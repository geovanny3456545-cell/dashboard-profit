import yfinance as yf
import pandas as pd
import numpy as np

def test_final_fix(symbol):
    ticker = symbol if symbol.endswith('.SA') else f"{symbol}.SA"
    print(f"\n--- Testing Fix for {ticker} (1W) ---")
    
    # Fetch 5y history
    data = yf.download(ticker, period="5y", interval="1wk", progress=False)
    if data.empty: return
    
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [c[0] for c in data.columns]
    
    # CLEAN BEFORE EMA
    cols_to_fix = ['Open', 'High', 'Low', 'Close']
    for col in cols_to_fix:
        if col in data.columns:
            # Using standard pandas way to avoid issues
            data[col] = data[col].replace(0, np.nan).ffill().bfill()
    
    # CALCULATE EMA
    data['EMA20'] = data['Close'].ewm(span=20, adjust=False).mean()
    
    print(f"Latest Close: {data['Close'].iloc[-1]:.4f}")
    print(f"Latest EMA 20: {data['EMA20'].iloc[-1]:.4f}")
    
    # check 8.58
    if np.isclose(data['EMA20'].iloc[-1], 8.58, atol=0.05):
        print("SUCCESS: EMA 20 is near 8.58!")
    else:
        print(f"DIFFERENCE: {data['EMA20'].iloc[-1] - 8.58:.4f}")

if __name__ == "__main__":
    test_final_fix("NATU3")
    test_final_fix("NTCO3")
