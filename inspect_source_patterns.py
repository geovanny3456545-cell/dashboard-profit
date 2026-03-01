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
        
        print(f"Total de linhas carregadas: {len(df)}")
        print("\nColunas encontradas:")
        print(df.columns.tolist())
        
        # Look for pattern columns
        setup_operado_col = next((c for c in df.columns if 'setup' in c.lower() and 'operado' in c.lower()), None)
        setup_real_col = next((c for c in df.columns if 'setup' in c.lower() and 'real' in c.lower()), None)
        
        if setup_operado_col:
            print(f"\nVariantes de 'Canal' em '{setup_operado_col}':")
            variants = [v for v in df[setup_operado_col].unique() if 'canal' in str(v).lower()]
            for v in variants:
                print(f"- {v}")
        
        if setup_real_col:
            print(f"\nVariantes de 'Canal' em '{setup_real_col}':")
            variants = [v for v in df[setup_real_col].unique() if 'canal' in str(v).lower()]
            for v in variants:
                print(f"- {v}")
                
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    inspect()
