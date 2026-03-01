import pandas as pd
from utils.data_loader import load_data
import streamlit as st

# Mock st.secrets
st.secrets = {
    "CSV_URL": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=872600748&single=true&output=csv",
    "PATTERN_URL": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=2017205813&single=true&output=csv"
}

def test_load():
    df, name_map = load_data()
    print("Columns after load_data():")
    print(df.columns.tolist())
    
    if not df.empty:
        print("\nFirst row sample (Numeric columns):")
        cols = [c for c in df.columns if 'Numeric' in c or 'Price' in c or 'Preço' in c]
        print(df[cols].iloc[0].to_dict())
        
        # Check specific columns I added
        print("\nChecking added columns:")
        for c in ['Preço Compra Numeric', 'Preço Venda Numeric']:
             if c in df.columns:
                  print(f"{c}: {df[c].iloc[0]} (Type: {type(df[c].iloc[0])})")
             else:
                  print(f"{c} MISSING!")

if __name__ == "__main__":
    test_load()
