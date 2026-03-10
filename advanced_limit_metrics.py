import pandas as pd
import requests
import io

def advanced_metrics():
    print("Iniciando análise de métricas avançadas...")
    PATTERN_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=2017205813&single=true&output=csv"
    
    r = requests.get(PATTERN_URL)
    df = pd.read_csv(io.StringIO(r.text))
    df.columns = [c.strip() for c in df.columns]
    
    mapping = {
        'Tipo de Ordem': 'Tipo_Ordem',
        'SETUP Operado': 'Setup_Operado',
        'SETUP Real': 'Ciclo_Real',
        'Res. Bruto': 'Profit_Str',
        'Teria Pagado': 'Teria_Pagado',
        'Observação': 'Obs'
    }
    for col in df.columns:
        if 'Teria' in col and 'Pagado' in col: mapping[col] = 'Teria_Pagado'
        if 'Observa' in col: mapping[col] = 'Obs'
        if 'Res' in col and 'Bruto' in col: mapping[col] = 'Profit_Str'
        if 'SETUP Real' in col: mapping[col] = 'Ciclo_Real'

    df = df.rename(columns=mapping)

    def clean_num(x):
        if pd.isna(x): return 0.0
        s = str(x).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
        try: return float(s)
        except: return 0.0

    df['Profit'] = df['Profit_Str'].apply(clean_num)
    df['Teria_Pagado'] = df['Teria_Pagado'].fillna('').astype(str).str.lower()
    
    # Analysis 2: Limit Orders vs Cycle (Strong Trend/Canal Estreito vs Others)
    limite_df = df[df['Tipo_Ordem'] == 'Ordem Limite'].copy()
    
    def get_context(val):
        v = str(val).lower()
        if 'estreito' in v or 'rompimento' in v: return 'Strong Trend (Danger for Limit)'
        if 'lateral' in v or 'amplo' in v: return 'Trading Range/Broad Channel (Safe for Limit)'
        return 'Other'

    limite_df['Context_Risk'] = limite_df['Ciclo_Real'].map(get_context)
    
    print("\n--- RISCO DE CONTEXTO EM ORDENS LIMITE (CICLO REAL) ---")
    context_stats = limite_df.groupby('Context_Risk')['Profit'].agg(['count', 'sum', 'mean']).reset_index()
    print(context_stats.to_string(index=False))

    # Analysis 3: The "Leaving Money on the Table" Metric
    # Identify trades where Profit <= 0 but Teria_Pagado contains 'sim'
    limite_df['Left_Money'] = (limite_df['Profit'] <= 0) & (limite_df['Teria_Pagado'].str.contains('sim'))
    
    missed_ops = limite_df[limite_df['Left_Money']]
    print(f"\n--- DINHEIRO DEIXADO NA MESA (ORDENS LIMITE) ---")
    print(f"Total de trades saindo no zero/negativo que PAGARIAM: {len(missed_ops)}")
    if len(missed_ops) > 0:
        # We don't have the 'intended' profit, but we know the count
        print("\nExemplos de trades 'Protegidos' cedo demais:")
        for idx, row in missed_ops.iterrows():
            print(f"Data: {row['Abertura']} | Profit Real: {row['Profit']} | Ciclo: {row['Ciclo_Real']}")
            print(f"  Obs: {row['Obs']}")
            print("-" * 20)

if __name__ == "__main__":
    advanced_metrics()
