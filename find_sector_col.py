import requests
import pandas as pd
import io

BASE_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub"
GID = '1798886578'

url = f"{BASE_URL}?gid={GID}&single=true&output=csv"
try:
    response = requests.get(url, timeout=10)
    response.encoding = 'utf-8'
    if response.status_code == 200:
        # Read with more columns to see everything
        df = pd.read_csv(io.StringIO(response.text), nrows=2)
        print(f"All columns found (raw): {df.columns.tolist()}")
        
        # Search for Sector/Setor in the first 50 rows in any column
        df_full = pd.read_csv(io.StringIO(response.text), nrows=50)
        for col in df_full.columns:
            if df_full[col].astype(str).str.contains('Setor|Setores', case=False).any():
                print(f"Found 'Setor' related content in column: {col}")
                print(df_full[col].head(10))
                
    else:
        print(f"GID: {GID} | Status Code: {response.status_code}")
except Exception as e:
    print(f"GID: {GID} | Error: {e}")
