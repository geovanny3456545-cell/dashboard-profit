import pandas as pd
import requests
import io
import datetime
import numpy as np

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=872600748&single=true&output=csv"
PATTERN_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=2017205813&single=true&output=csv"

def clean_money(val):
    if pd.isna(val) or val == '': return 0.0
    s_v = str(val).strip().replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
    try: return float(s_v)
    except: return 0.0

def get_df_perf():
    r = requests.get(CSV_URL)
    content = r.text
    lines = content.splitlines()
    header_idx = -1
    for i, line in enumerate(lines[:20]):
        if "Ativo" in line and ("Abertura" in line or "Data" in line):
            header_idx = i
            sep = ';' if line.count(';') > line.count(',') else ','
            break
    df = pd.read_csv(io.StringIO("\n".join(lines[header_idx:])), sep=sep)
    return df

def get_df_pattern():
    r = requests.get(PATTERN_URL)
    content = r.text
    lines = content.splitlines()
    sep = ';' if lines[0].count(';') > lines[0].count(',') else ','
    df = pd.read_csv(io.StringIO(content), sep=sep)
    return df

def analyze():
    print("Loading data...")
    df_perf = get_df_perf()
    df_pattern = get_df_pattern()

    # Column mapping
    perf_map = {}
    for c in df_perf.columns:
        cl = c.lower()
        if 'ativo' in cl and 'ag' not in cl: perf_map[c] = 'Ativo'
        elif 'abertura' in cl: perf_map[c] = 'Abertura'
        elif 'res' in cl and 'bruto' in cl: perf_map[c] = 'Profit'
    df_perf = df_perf.rename(columns=perf_map)
    df_perf['Profit'] = df_perf['Profit'].apply(clean_money)
    df_perf['Date'] = pd.to_datetime(df_perf['Abertura'].str.replace(',', ' '), dayfirst=True, errors='coerce')

    patt_map = {}
    for c in df_pattern.columns:
        cl = c.lower()
        if 'tipo' in cl and 'ordem' in cl: patt_map[c] = 'Tipo_Ordem'
        elif 'ativo' in cl: patt_map[c] = 'Ativo'
        elif 'abertura' in cl: patt_map[c] = 'Abertura'
        elif 'setup' in cl and 'operado' in cl: patt_map[c] = 'Pattern'
    df_pattern = df_pattern.rename(columns=patt_map)
    df_pattern['Date'] = pd.to_datetime(df_pattern['Abertura'].str.replace(',', ' '), dayfirst=True, errors='coerce')

    # Merge
    df_perf['Ativo_Base'] = df_perf['Ativo'].str.extract(r'^([A-Z]{3})')[0]
    df_pattern['Ativo_Base'] = df_pattern['Ativo'].str.extract(r'^([A-Z]{3})')[0]
    df_perf['Merge_Dt'] = df_perf['Date'].dt.floor('min')
    df_pattern['Merge_Dt'] = df_pattern['Date'].dt.floor('min')
    df_pattern_clean = df_pattern.drop_duplicates(subset=['Ativo_Base', 'Merge_Dt'], keep='last')
    df = df_perf.merge(df_pattern_clean[['Ativo_Base', 'Merge_Dt', 'Tipo_Ordem', 'Pattern']], on=['Ativo_Base', 'Merge_Dt'], how='left')

    # Ranges
    today = datetime.datetime(2026, 2, 27)
    week_start = today - datetime.timedelta(days=4) # Monday Feb 23 (approx)
    # Actually Monday Feb 23 is the correct start for a Monday-Friday week if Friday is Feb 27.
    month_start = datetime.datetime(2026, 2, 1)

    periods = {
        "WEEK": df[(df['Date'] >= week_start) & (df['Date'] <= today + datetime.timedelta(days=1))],
        "MONTH": df[(df['Date'] >= month_start) & (df['Date'] <= today + datetime.timedelta(days=1))]
    }

    for name, subset in periods.items():
        print(f"\n=== {name} ANALYSIS ===")
        print(f"Total Trades: {len(subset)}")
        print(f"Total Profit: R$ {subset['Profit'].sum():,.2f}")
        
        subset_orders = subset[subset['Tipo_Ordem'].isin(['Ordem Stop', 'Ordem Limite'])]
        if subset_orders.empty:
            print("No identified orders in this period.")
            continue
            
        stats = subset_orders.groupby('Tipo_Ordem')['Profit'].agg(['count', 'sum', 'mean']).reset_index()
        
        # Win Rate
        wr = subset_orders.groupby('Tipo_Ordem').apply(lambda x: (x['Profit'] > 0).mean() * 100, include_groups=False).reset_index(name='WinRate')
        stats = stats.merge(wr, on='Tipo_Ordem')
        
        print(stats.to_string(index=False))
        
        # Pattern analysis
        print("\nTop Patterns (Profit):")
        patt_stats = subset_orders.groupby(['Pattern', 'Tipo_Ordem'])['Profit'].sum().reset_index().sort_values('Profit', ascending=False)
        print(patt_stats.head(10).to_string(index=False))
        
        print("\nWorst Patterns (Profit):")
        print(patt_stats.tail(5).to_string(index=False))

if __name__ == "__main__":
    analyze()
