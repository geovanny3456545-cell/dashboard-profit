import yfinance as yf
import pandas as pd

def check_ntco3():
    ticker = "NTCO3.SA"
    print(f"--- Checking {ticker} ---")
    data = yf.download(ticker, period="max", interval="1wk", progress=False)
    if data.empty:
        print("Still no data for NTCO3.SA with period=max")
        return
        
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [c[0] for c in data.columns]
    
    data['EMA20'] = data['Close'].ewm(span=20, adjust=False).mean()
    print(f"Weekly EMA 20: {data['EMA20'].iloc[-1]:.4f}")
    print(f"Weekly Last Close: {data['Close'].iloc[-1]:.4f}")
    
    data_mo = yf.download(ticker, period="max", interval="1mo", progress=False)
    if not data_mo.empty:
        if isinstance(data_mo.columns, pd.MultiIndex):
            data_mo.columns = [c[0] for c in data_mo.columns]
        data_mo['EMA20'] = data_mo['Close'].ewm(span=20, adjust=False).mean()
        print(f"Monthly EMA 20: {data_mo['EMA20'].iloc[-1]:.4f}")

if __name__ == "__main__":
    check_ntco3()
