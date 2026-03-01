import requests
import pandas as pd
import io

BASE_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub"
CANDIDATES = ['1831587481', '1683453240', '1798886578']

for gid in CANDIDATES:
    url = f"{BASE_URL}?gid={gid}&single=true&output=csv"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Load with headers to see if column E, H, I match user description
            df = pd.read_csv(io.StringIO(response.text))
            print(f"\n--- GID: {gid} ---")
            print(f"Columns: {df.columns.tolist()}")
            print(f"Sample Data (last 5 rows):\n{df.tail()}")
        else:
            print(f"GID: {gid} | Status Code: {response.status_code}")
    except Exception as e:
        print(f"GID: {gid} | Error: {e}")
