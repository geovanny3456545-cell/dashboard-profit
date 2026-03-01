import pandas as pd
import requests
import io

PATTERN_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=2017205813&single=true&output=csv"

def inspect():
    try:
        response = requests.get(PATTERN_URL)
        response.raise_for_status()
        
        f = io.StringIO(response.text)
        content = f.read()
        f.seek(0)
        
        sep = ','
        if ';' in content and content.count(';') > content.count(','): sep = ';'
        
        df = pd.read_csv(f, sep=sep, on_bad_lines='skip')
        
        # Look for 'Tipo de Ordem' column
        col = next((c for c in df.columns if 'tipo' in c.lower() and 'ordem' in c.lower()), None)
        
        if col:
            print(f"\nValores únicos em '{col}':")
            print(df[col].unique().tolist())
        else:
            print("Coluna 'Tipo de Ordem' não encontrada.")
                
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    inspect()
