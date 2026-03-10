import pandas as pd
import numpy as np
import requests
import io

def detailed_analysis():
    CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=872600748&single=true&output=csv"
    PATTERN_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=2017205813&single=true&output=csv"

    def get_raw(url):
        r = requests.get(url)
        r.raise_for_status()
        return r.text

    perf_content = get_raw(CSV_URL)
    pattern_content = get_raw(PATTERN_URL)

    lines = perf_content.splitlines()
    header_idx = -1
    for i, line in enumerate(lines[:20]):
        if "Ativo" in line and ("Abertura" in line or "Data" in line):
            header_idx = i
            sep = ';' if line.count(';') > line.count(',') else ','
            break
    
    df = pd.read_csv(io.StringIO("\n".join(lines[header_idx:])), sep=sep, on_bad_lines='skip')
    df_p = pd.read_csv(io.StringIO(pattern_content), sep=';' if ';' in pattern_content else ',', on_bad_lines='skip')

    # Mapping
    df = df.rename(columns={c: 'Ativo' for c in df.columns if 'ativo' in c.lower() and 'ag' not in c.lower()})
    df = df.rename(columns={c: 'Abertura' for c in df.columns if 'abertura' in c.lower()})
    df = df.rename(columns={c: 'Res_Bruto' for c in df.columns if 'res' in c.lower() and 'bruto' in c.lower()})
    
    col_map_p = {}
    for c in df_p.columns:
        cl = c.lower()
        if 'tipo' in cl and 'ordem' in cl: col_map_p[c] = 'Tipo_Ordem'
        elif 'setup' in cl and 'operado' in cl: col_map_p[c] = 'Setup_Operado'
        elif 'setup' in cl and 'real' in cl: col_map_p[c] = 'Ciclo_Real'
        elif 'ativo' in cl: col_map_p[c] = 'Ativo'
        elif 'abertura' in cl: col_map_p[c] = 'Abertura'
        elif 'observa' in cl: col_map_p[c] = 'Obs'
        elif 'pagado' in cl: col_map_p[c] = 'Teria_Pagado'
    df_p = df_p.rename(columns=col_map_p)
    if 'Abertura' not in df_p.columns:
        print("Detected columns in df_p:", df_p.columns.tolist())
        # Fallback if specific header not found
        if not df_p.empty:
            df_p.columns = [str(c).strip() for c in df_p.columns]
            
    df['Abertura_Dt'] = pd.to_datetime(df['Abertura'].str.replace(',', ' '), dayfirst=True, errors='coerce')
    df_p['Abertura_Dt'] = pd.to_datetime(df_p['Abertura'].astype(str).str.replace(',', ' '), dayfirst=True, errors='coerce')
    df['Ativo_Base'] = df['Ativo'].str.extract(r'^([A-Z]{3})')[0]
    df_p['Ativo_Base'] = df_p['Ativo'].str.extract(r'^([A-Z]{3})')[0]
    df['Merge_Dt'] = df['Abertura_Dt'].dt.floor('min')
    df_p['Merge_Dt'] = df_p['Abertura_Dt'].dt.floor('min')
    
    df_p_clean = df_p.drop_duplicates(subset=['Ativo_Base', 'Merge_Dt'], keep='last')
    df = df.merge(df_p_clean[['Ativo_Base', 'Merge_Dt', 'Tipo_Ordem', 'Setup_Operado', 'Ciclo_Real', 'Obs', 'Teria_Pagado']], on=['Ativo_Base', 'Merge_Dt'], how='left')

    def clean_num(x):
        if isinstance(x, str): x = x.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
        try: return float(x)
        except: return 0.0

    df['Profit'] = df['Res_Bruto'].apply(clean_num)
    
    # Analysis 1: Limit Orders in Lateralidade
    limit_tr = df[(df['Tipo_Ordem'] == 'Ordem Limite') & (df['Setup_Operado'].str.contains('Lateral', na=False, case=False))]
    
    print("\n=== DETALHES DE ORDENS LIMITE EM LATERALIDADE ===")
    print(f"Total de trades: {len(limit_tr)}")
    print(f"Lucro Total: {limit_tr['Profit'].sum()}")
    print(f"Win Rate: {(limit_tr['Profit'] > 0).mean()*100:.1f}%")
    
    print("\n--- Exemplos de Trades Negativos com Limite em TR ---")
    neg_tr = limit_tr[limit_tr['Profit'] < 0].sort_values('Profit')
    for idx, row in neg_tr.head(10).iterrows():
        print(f"Data: {row['Abertura']} | Profit: {row['Profit']} | Real: {row['Ciclo_Real']} | Paid?: {row['Teria_Pagado']}")
        print(f"  Obs: {row['Obs']}")
        print("-" * 30)

    # Analysis 2: Stop Orders performance
    print("\n=== PERFORMANCE DE ORDENS STOP ===")
    stop_stats = df[df['Tipo_Ordem']=='Ordem Stop'].groupby('Setup_Operado')['Profit'].agg(['count', 'sum', 'mean']).reset_index()
    print(stop_stats.to_string(index=False))

    # Analysis 3: Compare "Teria Pagado Swing" vs "Real Outcome"
    df_swing = df[df['Teria_Pagado'].astype(str).str.contains('Sim', na=False, case=False)]
    print("\n=== TRADES QUE TERIAM PAGADO SWING ===")
    print(f"Total: {len(df_swing)}")
    print(f"Média de lucro real nesses trades: {df_swing['Profit'].mean()}")
    
    type_swing = df_swing.groupby('Tipo_Ordem')['Profit'].agg(['count', 'sum', 'mean']).reset_index()
    print(type_swing.to_string(index=False))

if __name__ == "__main__":
    detailed_analysis()
