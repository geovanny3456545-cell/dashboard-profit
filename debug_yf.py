import yfinance as yf
import pandas as pd

def debug_yf():
    ticker = "PETR4.SA"
    print(f"Downloading {ticker}...")
    data = yf.download(ticker, period="1mo", interval="1d", progress=False)
    print("\nColumns:", data.columns.tolist())
    print("\nIndex Name:", data.index.name)
    print("\nHead:\n", data.head())
    
    data_reset = data.reset_index()
    print("\nReset Index Columns:", data_reset.columns.tolist())

if __name__ == "__main__":
    debug_yf()
