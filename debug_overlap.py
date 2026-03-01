import pandas as pd
import requests
import io
import datetime

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=2017205813&single=true&output=csv"

try:
    print(f"Fetching data from {CSV_URL}...")
    response = requests.get(CSV_URL)
    response.raise_for_status()
    df = pd.read_csv(io.StringIO(response.text))
    
    # Clean columns
    df.columns = [c.replace('\n', ' ').strip() for c in df.columns]
    print(f"Columns: {df.columns.tolist()}")
    
    # Parse dates
    df['Abertura'] = pd.to_datetime(df['Abertura'], dayfirst=True, errors='coerce')
    
    # Filter for the specific date mentioned: 2026-01-19
    target_date = datetime.date(2026, 1, 19)
    df_day = df[df['Abertura'].dt.date == target_date].copy()
    
    if df_day.empty:
        print("No trades found for 2026-01-19")
    else:
        print(f"\nTrades on {target_date}: {len(df_day)}")
        print(df_day[['Abertura', 'Ativo', 'Res. Bruto', 'Lado', 'Qtd']].sort_values('Abertura').to_string())
        
        # Check for exact duplicates
        duplicates = df_day[df_day.duplicated(subset=['Abertura'], keep=False)]
        if not duplicates.empty:
            print("\n!!! POTENTIAL DUPLICATES OR SIMULTANEOUS TRADES DETECTED !!!")
            print(duplicates[['Abertura', 'Ativo', 'Res. Bruto']].sort_values('Abertura').to_string())
            
except Exception as e:
    print(f"Error: {e}")
