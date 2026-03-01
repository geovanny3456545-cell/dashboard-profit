import pandas as pd
import numpy as np
import requests
import io
import csv
import datetime
from utils.data_loader import load_data

def run_analysis():
    print("Carregando dados...")
    # Mocking streamlit to use load_data script-style if possible, 
    # but data_loader uses st.cache. Let's just manually load or use the logic.
    
    # Actually, load_data returns df, name_map
    # I'll manually implement the load logic to avoid streamlit errors in terminal
    
    CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=872600748&single=true&output=csv"
    PATTERN_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=2017205813&single=true&output=csv"

    def get_raw(url):
        r = requests.get(url)
        r.raise_for_status()
        return r.text

    print("Fetching performance report...")
    perf_content = get_raw(CSV_URL)
    print("Fetching patterns...")
    pattern_content = get_raw(PATTERN_URL)

    # Simplified parsing for analysis
    # Performance Report
    lines = perf_content.splitlines()
    header_idx = -1
    for i, line in enumerate(lines[:20]):
        if "Ativo" in line and ("Abertura" in line or "Data" in line):
            header_idx = i
            sep = ';' if line.count(';') > line.count(',') else ','
            break
    
    df = pd.read_csv(io.StringIO("\n".join(lines[header_idx:])), sep=sep)
    
    # Patterns
    lines_p = pattern_content.splitlines()
    sep_p = ';' if lines_p[0].count(';') > lines_p[0].count(',') else ','
    df_p = pd.read_csv(io.StringIO(pattern_content), sep=sep_p)

    # Column Mapping (following data_loader logic)
    name_map = {}
    found_qtd = False
    for c in df.columns:
        cl = c.lower().strip()
        if 'ativo' in cl and 'ag' not in cl: name_map[c] = 'Ativo'
        elif 'abertura' in cl: name_map[c] = 'Abertura'
        elif 'res' in cl and 'bruto' in cl: name_map[c] = 'Res_Bruto'
    df = df.rename(columns=name_map)

    col_map_p = {}
    for c in df_p.columns:
        cl = c.lower()
        if 'tipo' in cl and 'ordem' in cl: col_map_p[c] = 'Tipo_Ordem'
        elif 'ativo' in cl: col_map_p[c] = 'Ativo'
        elif 'abertura' in cl: col_map_p[c] = 'Abertura'
        elif 'setup' in cl and 'operado' in cl: col_map_p[c] = 'Pattern'
    df_p = df_p.rename(columns=col_map_p)

    # Merge logic
    df['Abertura_Dt'] = pd.to_datetime(df['Abertura'].str.replace(',', ' '), dayfirst=True, errors='coerce')
    df_p['Abertura_Dt'] = pd.to_datetime(df_p['Abertura'].str.replace(',', ' '), dayfirst=True, errors='coerce')
    
    df['Ativo_Base'] = df['Ativo'].str.extract(r'^([A-Z]{3})')[0]
    df_p['Ativo_Base'] = df_p['Ativo'].str.extract(r'^([A-Z]{3})')[0]
    
    df['Merge_Dt'] = df['Abertura_Dt'].dt.floor('min')
    df_p['Merge_Dt'] = df_p['Abertura_Dt'].dt.floor('min')
    
    df_p_clean = df_p.drop_duplicates(subset=['Ativo_Base', 'Merge_Dt'], keep='last')
    df = df.merge(df_p_clean[['Ativo_Base', 'Merge_Dt', 'Tipo_Ordem', 'Pattern']], on=['Ativo_Base', 'Merge_Dt'], how='left')

    # Data Clean
    def clean_num(x):
        if isinstance(x, str):
            x = x.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
        try:
            return float(x)
        except:
            return 0.0

    df['Profit'] = df['Res_Bruto'].apply(clean_num)
    df['Tipo_Ordem'] = df['Tipo_Ordem'].fillna('Não Identificado')

    # Filtering for defined orders
    df_analise = df[df['Tipo_Ordem'].isin(['Ordem Stop', 'Ordem Limite'])]

    print("\n--- PERFORMANCE POR TIPO DE ORDEM ---")
    stats = df_analise.groupby('Tipo_Ordem')['Profit'].agg(['count', 'sum', 'mean', 'median', 'std']).reset_index()
    
    # Win rate
    wr = df_analise.groupby('Tipo_Ordem').apply(lambda x: (x['Profit'] > 0).mean() * 100, include_groups=False).reset_index(name='WinRate_%')
    stats = stats.merge(wr, on='Tipo_Ordem')

    # Profit Factor
    def calc_pf(series):
        gains = series[series > 0].sum()
        losses = abs(series[series < 0].sum())
        return gains / losses if losses != 0 else np.inf

    pf = df_analise.groupby('Tipo_Ordem')['Profit'].apply(calc_pf).reset_index(name='ProfitFactor')
    stats = stats.merge(pf, on='Tipo_Ordem')

    print(stats.to_string(index=False))

    print("\n--- ANÁLISE DETALHADA: POR PATTERN ---")
    pattern_stats = df_analise.groupby(['Tipo_Ordem', 'Pattern'])['Profit'].agg(['count', 'sum', 'mean']).reset_index()
    pattern_stats = pattern_stats.sort_values(['Pattern', 'Tipo_Ordem'])
    print(pattern_stats.to_string(index=False))

    print("\n--- RESUMO EXECUTIVO ---")
    limit_prof = stats[stats['Tipo_Ordem']=='Ordem Limite']['sum'].values[0] if not stats[stats['Tipo_Ordem']=='Ordem Limite'].empty else 0
    stop_prof = stats[stats['Tipo_Ordem']=='Ordem Stop']['sum'].values[0] if not stats[stats['Tipo_Ordem']=='Ordem Stop'].empty else 0
    
    limit_count = stats[stats['Tipo_Ordem']=='Ordem Limite']['count'].values[0] if not stats[stats['Tipo_Ordem']=='Ordem Limite'].empty else 0
    stop_count = stats[stats['Tipo_Ordem']=='Ordem Stop']['count'].values[0] if not stats[stats['Tipo_Ordem']=='Ordem Stop'].empty else 0

    print(f"Total Lucro Limite: R$ {limit_prof:,.2f} ({limit_count} trades)")
    print(f"Total Lucro Stop:   R$ {stop_prof:,.2f} ({stop_count} trades)")
    
    if limit_prof < stop_prof:
        print("\nCONCLUSÃO PRELIMINAR: As ordens STOP estão performando melhor financeiramente.")
    else:
        print("\nCONCLUSÃO PRELIMINAR: As ordens LIMITE estão performando melhor financeiramente.")

if __name__ == "__main__":
    run_analysis()
