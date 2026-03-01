import requests
import io
import pandas as pd

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=872600748&single=true&output=csv"

def check_headers():
    r = requests.get(CSV_URL)
    content = r.text
    # Finding the header row using ProfitPro logic
    lines = content.splitlines()
    header_idx = -1
    for i, line in enumerate(lines):
         if 'Ativo' in line or 'Ativo' in line:
              header_idx = i
              break
    
    if header_idx != -1:
        df = pd.read_csv(io.StringIO("\n".join(lines[header_idx:])), sep=';')
        print("CSV Headers:")
        print(df.columns.tolist())
        print("\nFirst row sample:")
        print(df.iloc[0].to_dict())
    else:
        print("Could not find header row.")

if __name__ == "__main__":
    check_headers()
