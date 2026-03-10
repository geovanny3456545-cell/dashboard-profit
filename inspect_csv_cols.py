import pandas as pd
import requests
import io

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=872600748&single=true&output=csv"

def inspect():
    try:
        response = requests.get(CSV_URL)
        response.raise_for_status()
        
        f = io.StringIO(response.text)
        content = f.read()
        f.seek(0)
        
        sep = ','
        if ';' in content and content.count(';') > content.count(','): sep = ';'
        
        df = pd.read_csv(f, sep=sep, on_bad_lines='skip')
        print(df.columns.tolist())
                
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    inspect()
