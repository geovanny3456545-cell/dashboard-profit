import pandas as pd
import numpy as np
import sys
import os

# Set file path
FILE = r"g:\Meu Drive\Antigravity\Finançals Analysis (1)\trading_data_day_trade.csv"

def analyze_brooks():
    print("--- Al Brooks Performance Audit ---")
    
    # Load data
    try:
        df = pd.read_csv(FILE)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    # Map columns based on observed structure
    # Based on grep results, columns might need manual mapping if no header or if header is problematic
    cols = df.columns.tolist()
    print(f"Detected columns: {cols}")
    
    # Filtering for mismatches
    # I'll use index based access if column names are messy
    # 8: Operado, 9: Real, 14: Obs (0-indexed)
    
    # Let's try to identify by name if possible
    col_operado = 'Ciclo Operado'
    col_real = 'Ciclo Real'
    col_obs = 'Observação'
    col_res = 'Res. Líquido'
    
    # If they don't match exactly, find them
    def find_col(possible_names):
        for c in cols:
            for p in possible_names:
                if p.lower() in c.lower():
                    return c
        return None

    c_operado = find_col(['Operado', 'Ciclo Operado'])
    c_real = find_col(['Real', 'Ciclo Real'])
    c_obs = find_col(['Observa', 'Obs'])
    c_res = find_col(['Res', 'Líquido', 'Resultado'])

    if not all([c_operado, c_real, c_obs]):
        print("Required columns not found precisely. Using index-based access.")
        c_operado = cols[8]
        c_real = cols[9]
        c_obs = cols[14]
        c_res = cols[6]

    print(f"Using columns: Operado='{c_operado}', Real='{c_real}', Obs='{c_obs}'")

    # Clean Result column
    def clean_res(val):
        if pd.isna(val): return 0
        s = str(val).replace('R$', '').replace('.', '').replace(',', '.').replace(' ', '')
        try:
            return float(s)
        except:
            return 0

    df['Res_Numeric'] = df[c_res].map(clean_res)
    
    # Grouping Logic for Al Brooks Methodology
    # Group BTC: Breakout / Tight Channel (Urgency/Momentum)
    # Group TR: Trading Range (Value/Fading)
    # Group BC: Broad Channel (Trending but two-sided)
    
    def get_group(val):
        v = str(val).lower()
        if 'rompimento' in v or 'estreito' in v: return 'BTC (Momentum)'
        if 'lateral' in v or 'range' in v: return 'TR (Lateral)'
        if 'amplo' in v: return 'BC (Canal Amplo)'
        return 'Outro'

    df['Group_Operado'] = df[c_operado].map(get_group)
    df['Group_Real'] = df[c_real].map(get_group)
    
    # Mismatch Analysis based on Groups
    mismatches = df[df['Group_Operado'] != df['Group_Real']].copy()
    
    total_valid = len(df.dropna(subset=[c_operado, c_real]))
    match_rate = ((total_valid - len(mismatches)) / total_valid * 100) if total_valid > 0 else 0
    
    print(f"\nAlinhamento de Ciclos (BTC/TR/BC): {match_rate:.2f}%")
    print(f"Total de Desvios de Grupo: {len(mismatches)} / {total_valid}")
    
    print("\n--- Desvios de Grupo Detalhados ---")
    for idx, row in mismatches.iterrows():
        print(f"Trade {idx}:")
        print(f"  Operated: {row[c_operado]}")
        print(f"  Real Cycle: {row[c_real]}")
        print(f"  Result: {row[c_res]}")
        print(f"  Obs: {row[c_obs]}")
        print("-" * 30)

    # Keywords Analysis in Observations
    keywords = {
        "Impulsiva": ["impulsivo", "impulsiva", "ansiedade", "pressa"],
        "Atrasada": ["atrasado", "atrasada", "perdi o inicio", "perdi a entrada"],
        "Contra-Tendência": ["contra", "reversão", "retomada"],
        "FOMO/Chasing": ["chasing", "correndo", "persegui"],
        "Breakeven/Gestão": ["breakeven", "be", "sai cedo", "medo"],
        "Lateralidade": ["lateral", "tr", "trading range", "faixa"],
        "Rompimento": ["rompimento", "breakout"]
    }

    # Limit Order vs Cycle Analysis
    c_type = find_col(['Tipo', 'Ordem'])
    if not c_type: c_type = cols[7]
    
    print(f"\n--- Limit Order Context Analysis ---")
    limit_trades = df[df[c_type].astype(str).str.contains('Limite', na=False, case=False)]
    
    print(f"Total Limit Orders: {len(limit_trades)}")
    for ctx, count in limit_trades[c_real].value_counts().items():
        print(f"  Cycle '{ctx}': {count} trades")

    # Swing vs Scalp Analysis
    c_paid = find_col(['Pagado', 'Teria'])
    if not c_paid: c_paid = cols[13]
    
    print(f"\n--- Swing / Scalp Opportunity Analysis ---")
    swing_potential = df[df[c_paid].astype(str).str.contains('Sim', na=False, case=False)]
    
    missed_swings = swing_potential[df['Res_Numeric'] <= 0]
    print(f"Total Potential Swings (Teria Pagado): {len(swing_potential)}")
    print(f"Swings Missed (Result <= 0 but would have paid): {len(missed_swings)}")
    
    for idx, row in missed_swings.iterrows():
        print(f"  Trade {idx}: cycle={row[c_real]}, res={row[c_res]}, paid={row[c_paid]}, obs={row[c_obs]}")

    scalp_trades = df[df[c_paid].astype(str).str.contains('Scalp', na=False, case=False)]
    print(f"\nTrades focusing ONLY on Scalp: {len(scalp_trades)}")

if __name__ == "__main__":
    analyze_brooks()
