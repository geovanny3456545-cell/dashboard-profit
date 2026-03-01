import pandas as pd
import requests
import io

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=872600748&single=true&output=csv"
PATTERN_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=2017205813&single=true&output=csv"

def inspect(url, name):
    print(f"\n--- Inspecting {name} ---")
    try:
        response = requests.get(url)
        response.raise_for_status()
        f = io.StringIO(response.text)
        
        # Detect sep
        content = f.read()
        f.seek(0)
        sep = ','
        if ';' in content and content.count(';') > content.count(','): sep = ';'
        
        df = pd.read_csv(f, sep=sep, on_bad_lines='skip')
        print("Columns:", df.columns.tolist())
        print("First 3 rows:")
        print(df.head(3))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect(CSV_URL, "Consolidado")
    inspect(PATTERN_URL, "Operacoes")
