import pandas as pd
import requests
import io
import sys
import os

# Define absolute paths - UPDATED
base_dir = r"g:\Meu Drive\Antigravity\Finançals Analysis (1)"

# User provided URL (via GID extraction previously)
# GID for "OPERAÇÕES_DAY_TRADE": 2017205813
base_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub"
gid = "2017205813"
csv_url = f"{base_url}?gid={gid}&single=true&output=csv"

print(f"Attempting to fetch CSV from: {csv_url}")

try:
    response = requests.get(csv_url)
    response.raise_for_status()
    
    df = pd.read_csv(io.StringIO(response.text))
    
    print("\nDataFrame Info:")
    print(df.info())
    print("\nColumns:")
    print(df.columns.tolist())
    
    # Save the data
    output_path = os.path.join(base_dir, "trading_data_day_trade.csv")
    df.to_csv(output_path, index=False)
    print(f"\nSaved data to: {output_path}")

except Exception as e:
    print(f"CSV fetch failed: {e}")
