import streamlit as st
import pandas as pd
import numpy as np

# Mock st.secrets BEFORE importing data_loader
st.secrets = {
    "CSV_URL": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=872600748&single=true&output=csv",
    "PATTERN_URL": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=2017205813&single=true&output=csv"
}

from utils.data_loader import load_data

def test_load():
    df, name_map = load_data()
    print("Columns after load_data():")
    print(df.columns.tolist())
    
    if not df.empty:
        print("\nChecking added columns for first row:")
        # Show all numeric columns we care about
        check_cols = ['Preço Compra Numeric', 'Preço Venda Numeric', 'Res_Numeric']
        for c in check_cols:
             if c in df.columns:
                  print(f"{c}: {df[c].iloc[0]} (Type: {type(df[c].iloc[0])})")
             else:
                  print(f"{c} MISSING!")
                  
        print("\nSample of Preço Compra raw value if available:")
        if 'Preço Compra' in df.columns:
            print(f"Preço Compra RAW: {df['Preço Compra'].iloc[0]}")
        else:
            # Check for name mapping failure
            price_vars = [c for c in df.columns if 'Preço' in c or 'Price' in c]
            print(f"Other price-related columns: {price_vars}")

if __name__ == "__main__":
    test_load()
