import pandas as pd
import requests
import io

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=872600748&single=true&output=csv"

def analyze_day_trade_symbols():
    try:
        response = requests.get(CSV_URL)
        df = pd.read_csv(io.StringIO(response.text))
        
        if 'Ativo' in df.columns:
            print("Unique Symbols in Day Trade Tab:")
            print(df['Ativo'].unique())
            
            # Look at a few rows to see data format
            cols = ['Ativo', 'Abertura', 'Fechamento']
            valid_cols = [c for c in cols if c in df.columns]
            print("\nSample Data:")
            print(df[valid_cols].head(10))
        else:
            print(f"Column 'Ativo' not found. Columns are: {df.columns.tolist()}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_day_trade_symbols()
