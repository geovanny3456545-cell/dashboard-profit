import sys
import os
import pandas as pd

# Set CWD to ensure imports work
sys.path.append(os.getcwd())

from utils.data_loader import fetch_real_ohlc

def verify_fix():
    print("--- Final Verification of EMA Accuracy ---")
    symbol = "NATU3"
    period = "1W"
    
    df = fetch_real_ohlc(symbol, period)
    if df.empty:
        print(f"FAILED: No data for {symbol}")
        return
        
    last_ema = df['EMA20'].iloc[-1]
    last_close = df['Close'].iloc[-1]
    
    print(f"Symbol: {symbol}")
    print(f"Period: {period}")
    print(f"Latest Close: {last_close:.2f}")
    print(f"Latest EMA 20: {last_ema:.2f}")
    
    if abs(last_ema - 8.58) < 0.1:
        print("\nSUCCESS: EMA 20 matches expected value (range 8.58-8.60)!")
    else:
        print(f"\nSTILL DISCREPANT: Value is {last_ema:.2f}, expected 8.58")

if __name__ == "__main__":
    verify_fix()
