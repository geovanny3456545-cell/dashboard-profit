import pandas as pd
import os

base_dir = r"g:\Meu Drive\Antigravity\Finançals Analysis"
raw_path = os.path.join(base_dir, "consolidado_raw.csv")

try:
    # Read with semicolon delimiter, skipping first 4 rows
    df = pd.read_csv(raw_path, delimiter=';', skiprows=4, encoding='utf-8') # Encoding might be latin1 if from Profit, let's try utf-8 first (Google Sheet export is usually utf-8)
    
    print("Columns Found:")
    print(df.columns.tolist())
    
    print("\nFirst row of data:")
    print(df.iloc[0])
    
except Exception as e:
    print(f"Error: {e}")
