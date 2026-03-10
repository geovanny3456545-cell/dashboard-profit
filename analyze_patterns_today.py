import pandas as pd
import requests
import io
import datetime

PATTERN_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=2017205813&single=true&output=csv"

def analyze():
    resp = requests.get(PATTERN_URL)
    df = pd.read_csv(io.StringIO(resp.text))
    # Fix headers if there's a newline
    # Pandas usually joins them or handles it
    print("Columns:", df.columns.tolist())
    
    # Filter for today
    today_str = "23/02/2026"
    df['Abertura_Date'] = pd.to_datetime(df['Abertura'], dayfirst=True, errors='coerce')
    df_today = df[df['Abertura_Date'].dt.date == datetime.date(2026, 2, 23)].copy()
    
    print(f"Total entries today: {len(df_today)}")
    if not df_today.empty:
        print("\nDetail of entries:")
        for i, row in df_today.iterrows():
            print(f"--- Entry {i} ---")
            print(f"Ativo: {row['Ativo']}")
            print(f"Abertura: {row['Abertura']}")
            print(f"Setup Operado: {row['SETUP Operado']}")
            print(f"Setup Real: {row['SETUP Real']}")
            print(f"Observação: {row['Observação']}")
            print(f"Res. Bruto: {row['Res. Bruto']}")

if __name__ == "__main__":
    analyze()
