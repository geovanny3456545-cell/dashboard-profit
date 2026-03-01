import requests
import io
import pandas as pd

SHEET_ID = "2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz"
GIDS = ['1798886578', '471103982', '1683453240', '872600748', '871403186', '593269905', '2017205813']

for gid in GIDS:
    url = f"https://docs.google.com/spreadsheets/d/e/{SHEET_ID}/pub?gid={gid}&single=true&output=csv"
    print(f"\n--- Testing GID: {gid} ---")
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        content = resp.text
        if not content:
            print("Empty content")
            continue
            
        # Peek at columns
        f = io.StringIO(content)
        # Try to find header
        header = None
        for _ in range(10):
            line = f.readline()
            if not line: break
            if any(k in line.lower() for k in ['date', 'data', 'ativo', 'valor', 'd/w', 'status']):
                header = line
                break
        
        if header:
            print(f"Potential Header: {header.strip()}")
            # Show first row of data
            print(f"First line of data: {f.readline().strip()}")
        else:
            print(f"Could not identify header in first 10 lines. Raw snippet: {content[:100]}")
            
    except Exception as e:
        print(f"Error checking GID {gid}: {e}")
