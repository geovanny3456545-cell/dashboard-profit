import yfinance as yf
import datetime
import pandas as pd
from utils.data_loader import load_data
import streamlit as st

# Mock st.secrets
st.secrets = {
    "CSV_URL": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=872600748&single=true&output=csv",
    "PATTERN_URL": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=2017205813&single=true&output=csv"
}

def analyze_offset():
    df, _ = load_data()
    if df.empty:
        print("DF empty")
        return
        
    # Get a recent trade
    row = df.sort_values('Abertura_Dt', ascending=False).iloc[0]
    trade_dt = row['Abertura_Dt']
    report_price = row.get('Preço Compra Numeric', 0)
    
    print(f"Trade: {row['Ativo']} at {trade_dt}")
    print(f"Report Price: {report_price}")
    
    # Fetch proxy data
    symbol = "^BVSP"
    start = trade_dt - datetime.timedelta(minutes=30)
    end = trade_dt + datetime.timedelta(minutes=30)
    proxy_df = yf.download(symbol, start=start, end=end, interval='5m', progress=False)
    
    if not proxy_df.empty:
        proxy_price = proxy_df['Close'].iloc[0]
        print(f"Proxy (^BVSP) Price: {proxy_price}")
        print(f"DISCREPANCY (Report - Proxy): {report_price - proxy_price}")
    else:
        print("No proxy data found for this time.")

if __name__ == "__main__":
    analyze_offset()
