import yfinance as yf
import pandas as pd

def test_stability(symbol, interval_label, interval):
    ticker = symbol if symbol.endswith('.SA') else f"{symbol}.SA"
    print(f"\n--- {ticker} {interval_label} ---")
    
    # 1. Short history (40 bars)
    full_data = yf.download(ticker, period="10y", interval=interval, progress=False)
    if full_data.empty: return
    
    if isinstance(full_data.columns, pd.MultiIndex):
        full_data.columns = [c[0] for c in full_data.columns]
        
    short_data = full_data.tail(40).copy()
    short_data['EMA20'] = short_data['Close'].ewm(span=20, adjust=False).mean()
    
    # 2. Long history (Full)
    full_data['EMA20'] = full_data['Close'].ewm(span=20, adjust=False).mean()
    
    print(f"EMA 20 (Short history - 40 bars): {short_data['EMA20'].iloc[-1]:.4f}")
    print(f"EMA 20 (Full history): {full_data['EMA20'].iloc[-1]:.4f}")
    print(f"Last Close: {full_data['Close'].iloc[-1]:.4f}")

if __name__ == "__main__":
    for t in ["NATU3", "NTCO3"]:
        for il, i in [("1W", "1wk"), ("1M", "1mo")]:
            test_stability(t, il, i)
