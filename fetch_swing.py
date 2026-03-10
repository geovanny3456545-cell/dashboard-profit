import pandas as pd
import requests
import io
import os

# Configuration
SHEET_ID = "2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz"
GID = "1798886578" # OPERAÇÕES_SWING_TRADE
BASE_DIR = r"g:\Meu Drive\Antigravity\Finançals Analysis (1)"
OUTPUT_FILE = os.path.join(BASE_DIR, "trading_data_swing_trade.csv")

def fetch_swing_data():
    url = f"https://docs.google.com/spreadsheets/d/e/{SHEET_ID}/pub?gid={GID}&single=true&output=csv"
    print(f"Fetching Swing Trade data from: {url}")
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        # Read the CSV - Header is on row 0
        df = pd.read_csv(io.StringIO(response.text))
        
        # Basic cleanup: Rename unnamed columns if possible or just drop empty ones
        # Based on inspection:
        # Col 0: CONT
        # Col 1: DATA
        # Col 2: ATIVO
        # Col 3: empty?
        # Col 4: PERÍODO
        # Col 5: empty?
        # Col 6: ENTROU
        # Col 7: RESULTADO
        # Col 8: OBSERVAÇÃO
        # Col 9: OBSERVAÇÃO 2
        
        # Rename columns for consistency
        new_cols = ['ID', 'Data', 'Ativo', 'Extra1', 'Periodo', 'Extra2', 'Entrou', 'Resultado', 'Obs1', 'Obs2']
        if len(df.columns) == len(new_cols):
            df.columns = new_cols
        
        # Save to CSV
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"Successfully saved {len(df)} rows to {OUTPUT_FILE}")
        return True
        
    except Exception as e:
        print(f"Error fetching swing data: {e}")
        return False

if __name__ == "__main__":
    fetch_swing_data()
