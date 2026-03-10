import requests
import pandas as pd
import io

BASE_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub"
GIDS = ['1831587481', '1683453240', '2017205813', '872600748', '471103982', '1798886578', '871403186', '593269905']

for gid in GIDS:
    url = f"{BASE_URL}?gid={gid}&single=true&output=csv"
    try:
        # Fetch just the first few lines to get headers and some data
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text), nrows=2)
            print(f"GID: {gid} | Columns: {df.columns.tolist()}")
        else:
            print(f"GID: {gid} | Status Code: {response.status_code}")
    except Exception as e:
        print(f"GID: {gid} | Error: {e}")
