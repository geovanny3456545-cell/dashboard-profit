import requests
import pandas as pd
import io

BASE_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub"
GIDS = ['872600748', '593269905', '1683453240', '1798886578', '2017205813', '471103982', '1831587481', '871403186']

for gid in GIDS:
    url = f"{BASE_URL}?gid={gid}&single=true&output=csv"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            # Read first 50 rows to find header/data
            df = pd.read_csv(io.StringIO(r.text), header=None, nrows=50)
            print(f"\n--- GID: {gid} ---")
            # Search for "Saldo" or a date-like string or "D/W"
            for i, row in df.iterrows():
                row_str = " | ".join(map(str, row.values))
                if "Saldo" in row_str or "R$" in row_str or "2026" in row_str:
                    print(f"Row {i}: {row_str}")
        else:
            print(f"GID: {gid} | Status: {r.status_code}")
    except Exception as e:
        print(f"GID: {gid} | Error: {e}")
