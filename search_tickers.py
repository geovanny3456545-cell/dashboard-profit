import yfinance as yf

def search_symbols():
    queries = ['WING25', 'WIN=F', 'WING', 'MINI IBOVESPA', 'MINI DOLAR', 'WDO=F']
    for q in queries:
        print(f"\nSearching for '{q}':")
        try:
            # yfinance doesn't have a direct search but we can try to get info
            ticker = yf.Ticker(q)
            print(f"Info for {q}: {ticker.info.get('longName', 'N/A')}")
        except:
            print(f"No info for {q}")

if __name__ == "__main__":
    search_symbols()
