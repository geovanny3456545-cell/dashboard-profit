import requests
import pandas as pd
import io

BASE_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub"
GID = '2017205813' # Day Trade

url = f"{BASE_URL}?gid={GID}&single=true&output=csv"
try:
    response = requests.get(url, timeout=10)
    response.encoding = 'utf-8'
    if response.status_code == 200:
        df = pd.read_csv(io.StringIO(response.text), nrows=2)
        print(f"GID: {GID} | Columns: {df.columns.tolist()}")
    else:
        print(f"GID: {GID} | Status Code: {response.status_code}")
except Exception as e:
    print(f"GID: {GID} | Error: {e}")
