import pandas as pd
import requests
import io

GIDS = {
    'Current_Dash': '2017205813',
    'Consolidado_Maybe': '872600748'
}
BASE_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid={}&single=true&output=csv"

for name, gid in GIDS.items():
    print(f"\n--- Checking {name} (GID: {gid}) ---")
    try:
        url = BASE_URL.format(gid)
        resp = requests.get(url)
        resp.raise_for_status()
        
        # Try finding the specific 05/02 row
        # Read as text first to see format
        lines = resp.text.splitlines()[:5]
        print(f"First 5 lines:\n" + "\n".join(lines))
        
        if name == 'Consolidado_Maybe':
             # It might be semicolon separated
             df = pd.read_csv(io.StringIO(resp.text), sep=';', on_bad_lines='skip')
             print("Parsed with semi-colon:")
             print(df.columns.tolist())
             # Look for 05/02
             # Format in raw might be different
             pass
        else:
             df = pd.read_csv(io.StringIO(resp.text))
             
    except Exception as e:
        print(f"Error: {e}")
