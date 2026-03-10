import pandas as pd
import requests
import io

def check_gid(gid, name):
    url = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid={gid}&single=true&output=csv"
    try:
        r = requests.get(url)
        r.raise_for_status()
        
        # Simple line read first
        lines = r.text.splitlines()
        print(f"\n--- {name} (GID {gid}) ---")
        
        # Try to find header (Consolidado has metadata)
        header_row = 0
        for i, line in enumerate(lines[:20]):
            if "Ativo" in line or "Padrão" in line or "Abertura" in line:
                header_row = i
                print(f"Header found at line {i}: {line}")
                break
        
        # Read DF with found header
        df = pd.read_csv(io.StringIO("\n".join(lines[header_row:])), sep=';')
        print("Columns:", df.columns.tolist())
        print("Head(1):", df.head(1).to_dict('records'))
        
    except Exception as e:
        print(f"Error {name}: {e}")

check_gid("872600748", "Consolidado")
check_gid("2017205813", "Operações Day Trade")
