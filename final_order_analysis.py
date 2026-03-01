import pandas as pd
import requests
import io

def final_analysis():
    print("Iniciando análise final...")
    CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=872600748&single=true&output=csv"
    PATTERN_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=2017205813&single=true&output=csv"

    def fetch_df(url):
        r = requests.get(url)
        # Force CSV loading with comma first, fallback to semicolon
        try:
            return pd.read_csv(io.StringIO(r.text), sep=',')
        except:
            return pd.read_csv(io.StringIO(r.text), sep=';')

    df_raw = fetch_df(CSV_URL)
    df_p = fetch_df(PATTERN_URL)

    # Standardize columns for df_p
    p_map = {
        'Tipo de Ordem': 'Tipo_Ordem',
        'SETUP Operado': 'Setup_Operado',
        'SETUP Real': 'Ciclo_Real',
        'Abertura': 'Abertura',
        'Ativo': 'Ativo',
        'Observa\u00e7\u00e3o': 'Obs',
        'Observação': 'Obs',
        'Teria\nPagado': 'Teria_Pagado',
        'Teria Pagado': 'Teria_Pagado'
    }
    df_p = df_p.rename(columns=p_map)
    
    # Standardize columns for df_raw
    # Find column with 'res' and 'bruto'
    res_col = [c for c in df_raw.columns if 'res' in c.lower() and 'bruto' in c.lower()]
    if res_col: df_raw = df_raw.rename(columns={res_col[0]: 'Profit_Raw'})
    
    abr_col = [c for c in df_raw.columns if 'abertura' in c.lower() or 'data' in c.lower()]
    if abr_col: df_raw = df_raw.rename(columns={abr_col[0]: 'Abertura'})

    # Clean profit
    def clean_p(x):
        if pd.isna(x): return 0.0
        s = str(x).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
        try: return float(s)
        except: return 0.0
    
    df_raw['Profit'] = df_raw['Profit_Raw'].apply(clean_p)
    df_p['Profit_P'] = df_p['Res. Bruto'].apply(clean_p)

    # Analysis
    print("\n--- RESUMO POR TIPO DE ORDEM (DO PATTERN SHEET) ---")
    summary = df_p.groupby('Tipo_Ordem')['Profit_P'].agg(['count', 'sum', 'mean']).reset_index()
    print(summary.to_string(index=False))

    print("\n--- ORDENS LIMITE: POR SETUP ---")
    limite_df = df_p[df_p['Tipo_Ordem'] == 'Ordem Limite']
    limite_setup = limite_df.groupby('Setup_Operado')['Profit_P'].agg(['count', 'sum', 'mean']).reset_index()
    print(limite_setup.to_string(index=False))

    print("\n--- CASOS ONDE 'TERIA PAGADO SWING' ---")
    # Clean Teria_Pagado
    df_p['Teria_Pagado'] = df_p['Teria_Pagado'].fillna('').astype(str).str.lower()
    paid_swing = df_p[df_p['Teria_Pagado'].str.contains('sim')]
    
    paid_summary = paid_swing.groupby('Tipo_Ordem')['Profit_P'].agg(['count', 'sum', 'mean']).reset_index()
    print(paid_summary.to_string(index=False))

    print("\n--- DETALHES DE LOSS EM ORDENS LIMITE ---")
    loss_limite = limite_df[limite_df['Profit_P'] < 0].sort_values('Profit_P')
    for idx, row in loss_limite.iterrows():
        print(f"Setup: {row['Setup_Operado']} | Profit: {row['Profit_P']} | Obs: {row['Obs']}")

if __name__ == "__main__":
    final_analysis()
