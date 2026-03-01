import requests

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=872600748&single=true&output=csv"

try:
    response = requests.get(CSV_URL)
    response.raise_for_status()
    response.encoding = 'utf-8'
    
    lines = response.text.splitlines()
    print(f"Total lines: {len(lines)}")
    print("--- First 20 lines ---")
    for i, line in enumerate(lines[:20]):
        print(f"{i}: {line}")
        
except Exception as e:
    print(f"Error: {e}")
