import yfinance as yf
import pandas as pd

def debug_nflx():
    ticker = "NFLX34.SA"
    print(f"--- Debugging {ticker} Weekly ---")
    data = yf.download(ticker, period="6mo", interval="1wk", progress=False)
    
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    data.columns.name = None
    
    print("\nLast 5 Weekly Candles:")
    print(data.tail(5))
    
    print("\n--- Current Price Info ---")
    tick = yf.Ticker(ticker)
    info = tick.info
    print(f"Current Price (Regular): {info.get('regularMarketPrice')}")
    print(f"Previous Close: {info.get('previousClose')}")

if __name__ == "__main__":
    debug_nflx()
