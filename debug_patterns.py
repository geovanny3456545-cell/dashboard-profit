
import requests
import pandas as pd
import io

PATTERN_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=2017205813&single=true&output=csv"

try:
    print(f"Fetching {PATTERN_URL}...")
    response = requests.get(PATTERN_URL)
    response.raise_for_status()
    
    content = response.text
    print(f"Content length: {len(content)}")
    print("First 500 chars:")
    print(content[:500])
    
    # Try parsing
    f = io.StringIO(content)
    sep = ','
    if ';' in content and content.count(';') > content.count(','): sep = ';'
    
    df = pd.read_csv(f, sep=sep, on_bad_lines='skip')
    print("\nColumns found:")
    for c in df.columns:
        print(f" - '{c}'")
        
    print("\nRow 1:")
    print(df.head(1).to_dict())

except Exception as e:
    print(f"Error: {e}")
