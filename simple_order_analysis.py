import pandas as pd
import requests
import io

def final_analysis():
    print("Iniciando análise...")
    PATTERN_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=2017205813&single=true&output=csv"
    
    r = requests.get(PATTERN_URL)
    df = pd.read_csv(io.StringIO(r.text))

    # Clean column names (strip whitespace and handle common variations)
    df.columns = [c.strip() for c in df.columns]
    
    # Map essential columns
    mapping = {
        'Tipo de Ordem': 'Tipo_Ordem',
        'SETUP Operado': 'Setup',
        'Res. Bruto': 'Profit_Str',
        'Teria Pagado': 'Teria_Pagado',
        'Observação': 'Obs'
    }
    # Some columns might have weird characters or newlines
    for col in df.columns:
        if 'Teria' in col and 'Pagado' in col: mapping[col] = 'Teria_Pagado'
        if 'Observa' in col: mapping[col] = 'Obs'
        if 'Res' in col and 'Bruto' in col: mapping[col] = 'Profit_Str'

    df = df.rename(columns=mapping)

    def clean_num(x):
        if pd.isna(x): return 0.0
        s = str(x).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
        try: return float(s)
        except: return 0.0

    df['Profit'] = df['Profit_Str'].apply(clean_num)
    
    print("\n--- PERFORMANCE POR TIPO DE ORDEM ---")
    stats = df.groupby('Tipo_Ordem')['Profit'].agg(['count', 'sum', 'mean']).reset_index()
    print(stats.to_string(index=False))

    print("\n--- PERFORMANCE ORDENS LIMITE POR SETUP ---")
    limit_stats = df[df['Tipo_Ordem'] == 'Ordem Limite'].groupby('Setup')['Profit'].agg(['count', 'sum', 'mean']).reset_index()
    print(limit_stats.to_string(index=False))

    print("\n--- PERFORMANCE ORDENS STOP POR SETUP ---")
    stop_stats = df[df['Tipo_Ordem'] == 'Ordem Stop'].groupby('Setup')['Profit'].agg(['count', 'sum', 'mean']).reset_index()
    print(stop_stats.to_string(index=False))

    print("\n--- ANALISE 'TERIA PAGADO SWING' ---")
    df['Teria_Pagado'] = df['Teria_Pagado'].fillna('').astype(str).str.lower()
    swing_ok = df[df['Teria_Pagado'].str.contains('sim')]
    print(f"Total de trades que 'Teria Pagado': {len(swing_ok)}")
    swing_stats = swing_ok.groupby('Tipo_Ordem')['Profit'].agg(['count', 'sum', 'mean']).reset_index()
    print(swing_stats.to_string(index=False))

    print("\n--- TRADES COM LOSS EM ORDENS LIMITE ---")
    limit_loss = df[(df['Tipo_Ordem'] == 'Ordem Limite') & (df['Profit'] < 0)].sort_values('Profit')
    for idx, row in limit_loss.iterrows():
        print(f"Setup: {row['Setup']} | Profit: {row['Profit']} | Obs: {row['Obs']}")

if __name__ == "__main__":
    final_analysis()
