import pandas as pd
import requests
import io
import sys
import os

# Define absolute paths
base_dir = r"g:\Meu Drive\Antigravity\Finançals Analysis (1)"

# Consolidado GID
gid = "872600748"
base_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub"
csv_url = f"{base_url}?gid={gid}&single=true&output=csv"

print(f"Fetching Consolidado from: {csv_url}")

try:
    response = requests.get(csv_url)
    response.raise_for_status()
    
    # Save raw for inspection
    raw_path = os.path.join(base_dir, "consolidado_raw.csv")
    with open(raw_path, 'wb') as f:
        f.write(response.content)
    
    print(f"Saved raw data to {raw_path}")
    
    # Try parsing
    df = pd.read_csv(io.StringIO(response.text))
    print("Top 5 lines:")
    print(df.head())
    print("Columns:", df.columns.tolist())

except Exception as e:
    print(f"Fetch failed: {e}")
