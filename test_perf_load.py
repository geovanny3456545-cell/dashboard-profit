import requests
import io
import csv
import pandas as pd

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=872600748&single=true&output=csv"

def test_perf_load():
    response = requests.get(CSV_URL)
    response.encoding = 'utf-8'
    content = response.text
    
    lines = content.splitlines()
    header_idx = -1
    for i, line in enumerate(lines[:20]):
        if "ativo" in line.lower() and ("abertura" in line.lower() or "data" in line.lower()):
            header_idx = i
            print(f"Match found at line {i}: {line[:100]}")
            break
            
    if header_idx == -1:
        print("Header not found!")
        return

    sep = ';' if content.count(';') > content.count(',') else ','
    print(f"Detected sep: '{sep}'")
    
    f = io.StringIO(content)
    for _ in range(header_idx): f.readline()
    
    df = pd.read_csv(f, sep=sep, quoting=csv.QUOTE_NONE, on_bad_lines='skip')
    print(f"DF Columns: {df.columns.tolist()}")
    print(f"DF Shape before cleanup: {df.shape}")
    
    # Let's see the first row
    if not df.empty:
        print("First row:")
        print(df.iloc[0])
    else:
        print("DF is EMPTY after read_csv")

if __name__ == "__main__":
    test_perf_load()
