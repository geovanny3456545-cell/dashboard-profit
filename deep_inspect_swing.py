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
        # Read the first 50 rows to see if there's a header offset
        df = pd.read_csv(io.StringIO(response.text), nrows=50)
        print(f"\n--- GID: {GID} ---")
        print("First 20 lines of raw text:")
        print("\n".join(response.text.splitlines()[:20]))
        print("\nDataFrame sample (first 10 rows):")
        print(df.head(10))
    else:
        print(f"GID: {GID} | Status Code: {response.status_code}")
except Exception as e:
    print(f"GID: {GID} | Error: {e}")
