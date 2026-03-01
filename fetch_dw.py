import requests
import io
import pandas as pd

SHEET_ID = "2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz"
GID = "1683453240"

url = f"https://docs.google.com/spreadsheets/d/e/{SHEET_ID}/pub?gid={GID}&single=true&output=csv"

try:
    print(f"Fetching GID {GID}...")
    resp = requests.get(url)
    resp.raise_for_status()
    
    # Save raw for inspection
    with open("dw_consolidado_raw.csv", "w", encoding="utf-8") as f:
        f.write(resp.text)
        
    print("Saved to dw_consolidado_raw.csv")
    
    # Try parsing
    # Since it had "ESTRATÉGIA" at the top, it might have empty rows or headers late
    lines = resp.text.splitlines()
    for i, line in enumerate(lines[:20]):
        print(f"L{i}: {line}")

except Exception as e:
    print(f"Error: {e}")
