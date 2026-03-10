import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

def test_mt5():
    if not mt5.initialize():
        print("initialize() failed, error code =", mt5.last_error())
        # Try to find common symbols if initialized
        return

    print("MT5 version:", mt5.version())
    
    # Try to find WIN or WDO symbols
    symbols = mt5.symbols_get()
    win_symbols = [s.name for s in symbols if 'WIN' in s.name][:5]
    wdo_symbols = [s.name for s in symbols if 'WDO' in s.name][:5]
    
    print("WIN symbols found:", win_symbols)
    print("WDO symbols found:", wdo_symbols)
    
    if win_symbols:
        symbol = win_symbols[0]
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 10)
        if rates is not None:
             df = pd.DataFrame(rates)
             print(f"\nLast 10 bars for {symbol} (5m):")
             print(df.head())
        else:
             print(f"Failed to get rates for {symbol}")

    mt5.shutdown()

if __name__ == "__main__":
    test_mt5()
