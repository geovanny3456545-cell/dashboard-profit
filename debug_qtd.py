import requests

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=872600748&single=true&output=csv"

try:
    response = requests.get(CSV_URL)
    response.raise_for_status()
    lines = response.text.splitlines()
    
    # Header
    header_row = -1
    for i, line in enumerate(lines):
        if "Ativo" in line and "Abertura" in line:
            header_row = i
            break
            
    if header_row != -1:
        headers = lines[header_row].split(';')
        print(f"Headers (Raw): {headers}")
        
        # Data
        for j, line in enumerate(lines[header_row+1:header_row+5]):
            print(f"\nRow {j}: {line}")
            parts = line.split(';')
            # Print index and value for Qtd-like columns
            for idx, h in enumerate(headers):
                if 'Qtd' in h:
                    val = parts[idx] if idx < len(parts) else "MISSING"
                    print(f"  {h} [{idx}]: '{val}'")

except Exception as e:
    print(e)
