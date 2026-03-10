import pandas as pd
import requests
import io
import csv

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=872600748&single=true&output=csv"

def get_raw_report():
    r = requests.get(CSV_URL)
    r.encoding = 'utf-8'
    return r.text

def analyze():
    content = get_raw_report()
    lines = content.splitlines()
    header_idx = -1
    for i, line in enumerate(lines[:30]):
        l = line.lower()
        if "ativo" in l and ("abertura" in l or "data" in l):
            header_idx = i
            break
            
    if header_idx == -1:
        print("Header not found")
        return
        
    f = io.StringIO(content)
    for _ in range(header_idx): f.readline()
    df = pd.read_csv(f, sep=';' if content.count(';') > content.count(',') else ',')
    
    # Map to 'Ativo'
    name_map = {}
    for c in df.columns:
        if 'ativo' in c.lower() and 'ag' not in c.lower():
            name_map[c] = 'Ativo'
            break
            
    if 'Ativo' in name_map.values():
        df = df.rename(columns=name_map)
        print("Unique Day Trade Symbols:")
        print(df['Ativo'].unique())
        print("\nFirst 5 rows:")
        print(df[['Ativo']].head())
    else:
        print("Column 'Ativo' mapping failed")
        print(df.columns.tolist())

if __name__ == "__main__":
    analyze()
