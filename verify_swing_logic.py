import pandas as pd
from utils.data_loader import load_swing_trade_data
from utils.sector_map import get_sector

def verify():
    print("Testing load_swing_trade_data()...")
    df = load_swing_trade_data()
    if df.empty:
        print("Error: DataFrame is empty.")
        return
    
    print(f"Loaded {len(df)} rows.")
    print("Columns:", df.columns.tolist())
    print("Sample Data:")
    print(df.tail())
    
    print("\nTesting Sector Logic...")
    active_mask = (df['Entrou'].str.upper() == 'SIM') & (df['Resultado'].isin(['-', '', 'NAN', None]))
    active_positions = df[active_mask].copy()
    if not active_positions.empty:
        active_positions['Setor'] = active_positions['Ativo'].apply(get_sector)
        print("Active Positions Sectors:")
        print(active_positions[['Ativo', 'Setor']])
        
        sector_counts = active_positions['Setor'].value_counts()
        conflicts = sector_counts[sector_counts > 1]
        if not conflicts.empty:
            print(f"CONFLICT DETECTED in Sectors: {conflicts.index.tolist()}")
        else:
            print("No sector conflicts in active positions.")
    else:
        print("No active positions found to test sector conflicts.")

if __name__ == "__main__":
    verify()
