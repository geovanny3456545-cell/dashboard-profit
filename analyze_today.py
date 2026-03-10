import pandas as pd
import requests
import io
import datetime
import csv

# URLs from data_loader.py
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=872600748&single=true&output=csv"
PATTERN_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=2017205813&single=true&output=csv"

def clean_money(val):
    if pd.isna(val) or val == '': return 0.0
    s_v = str(val).strip().replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
    try:
        return float(s_v)
    except:
        return 0.0

def robust_load(url):
    resp = requests.get(url)
    content = resp.text
    lines = content.splitlines()
    
    header_idx = -1
    sep = ';' 
    for i, line in enumerate(lines[:20]):
        l_low = line.lower()
        if "ativo" in l_low and ("abertura" in l_low or "data" in l_low):
            header_idx = i
            sep = ';' if line.count(';') > line.count(',') else ','
            break
            
    if header_idx == -1:
        # Try finding by any common column
        for i, line in enumerate(lines[:20]):
            if "Ativo" in line or "Abertura" in line:
                header_idx = i
                sep = ';' if line.count(';') > line.count(',') else ','
                break

    if header_idx == -1: return pd.DataFrame()
    
    f = io.StringIO(content)
    for _ in range(header_idx): f.readline()
    
    # Read headers
    header_line = f.readline().strip()
    reader_h = csv.reader(io.StringIO(header_line), delimiter=sep)
    headers = next(reader_h)
    
    # Read data
    reader_d = csv.reader(f, delimiter=sep)
    data = []
    for row in reader_d:
        if row and row[0].strip():
            # Pad or truncate row to match headers
            if len(row) < len(headers):
                row = row + [''] * (len(headers) - len(row))
            else:
                row = row[:len(headers)]
            data.append(row)
            
    return pd.DataFrame(data, columns=headers)

def analyze_today():
    today_dt = datetime.date(2026, 2, 23)
    print(f"Analyzing data for {today_dt}...")

    # Fetch Performance Report
    print("Fetching Performance Report...")
    df_perf = robust_load(CSV_URL)
    
    if df_perf.empty:
        print("Failed to load Performance Report.")
    else:
        date_col = next((c for c in df_perf.columns if 'abertura' in c.lower()), None)
        if date_col:
            df_perf['Date_Parsed'] = pd.to_datetime(df_perf[date_col].str.replace(',', ' '), dayfirst=True, errors='coerce')
            df_today_perf = df_perf[df_perf['Date_Parsed'].dt.date == today_dt].copy()
            print(f"Found {len(df_today_perf)} trades for today.")
            
            if not df_today_perf.empty:
                pnl_col = next((c for c in df_today_perf.columns if 'res' in c.lower() and 'bruto' in c.lower()), None)
                if pnl_col:
                    df_today_perf['PnL'] = df_today_perf[pnl_col].apply(clean_money)
                    total_pnl = df_today_perf['PnL'].sum()
                    print(f"Total PnL: R$ {total_pnl:,.2f}")
                    
                    wins = df_today_perf[df_today_perf['PnL'] > 0]
                    losses = df_today_perf[df_today_perf['PnL'] < 0]
                    zeros = df_today_perf[df_today_perf['PnL'] == 0]
                    print(f"Wins: {len(wins)} | Losses: {len(losses)} | Even: {len(zeros)}")
                    print(f"Win Rate: {len(wins)/len(df_today_perf)*100:.1f}%")
                    
                    # Assets
                    ativo_col = next((c for c in df_today_perf.columns if 'ativo' in c.lower() and 'ag' not in c.lower()), 'Ativo')
                    print("\nTrades per Asset:")
                    print(df_today_perf[ativo_col].value_counts())
        else:
            print("Date column not found in Performance Report.")

    # Fetch Pattern Sheet
    print("\nFetching Pattern Sheet...")
    df_pattern = robust_load(PATTERN_URL)
    if not df_pattern.empty:
        p_date_col = next((c for c in df_pattern.columns if 'abertura' in c.lower()), None)
        if p_date_col:
            df_pattern['Date_Parsed'] = pd.to_datetime(df_pattern[p_date_col].astype(str).str.replace(',', ' '), dayfirst=True, errors='coerce')
            df_today_pattern = df_pattern[df_pattern['Date_Parsed'].dt.date == today_dt]
            print(f"Found {len(df_today_pattern)} classification entries.")
            
            if not df_today_pattern.empty:
                setup_col = next((c for c in df_today_pattern.columns if 'setup' in c.lower() and 'operado' in c.lower()), None)
                if setup_col:
                    print("\nSetups used today:")
                    print(df_today_pattern[setup_col].value_counts())
                
                obs_col = next((c for c in df_today_pattern.columns if any(x in c.lower() for x in ['observa', 'note', 'coment'])), None)
                if obs_col:
                    print("\nKey observations:")
                    for obs in df_today_pattern[obs_col].dropna().unique():
                        if obs and str(obs).strip():
                            print(f"- {obs}")
        else:
            print("Date column not found in Pattern Sheet.")

if __name__ == "__main__":
    analyze_today()
