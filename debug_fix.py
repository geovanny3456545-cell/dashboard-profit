import pandas as pd
import requests
import io

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=2017205813&single=true&output=csv"

try:
    print(f"Fetching data...")
    response = requests.get(CSV_URL)
    response.raise_for_status()
    df = pd.read_csv(io.StringIO(response.text))
    df.columns = [c.replace('\n', ' ').strip() for c in df.columns]
    
    # Parse
    df['Abertura_Raw'] = df['Abertura']
    df['Fechamento_Raw'] = df['Fechamento']
    
    df['Abertura'] = pd.to_datetime(df['Abertura'], dayfirst=True, errors='coerce')
    df['Fechamento'] = pd.to_datetime(df['Fechamento'], dayfirst=True, errors='coerce')
    
    # Calc Duration
    df['Duration'] = df['Fechamento'] - df['Abertura']
    
    # Find Negative Duration
    neg_dur = df[df['Duration'] < pd.Timedelta(0)]
    
    if not neg_dur.empty:
        print("\n!!! NEGATIVE DURATION ROWS !!!")
        print(neg_dur[['Abertura_Raw', 'Fechamento_Raw', 'Abertura', 'Fechamento', 'Duration']].to_string())
    else:
        print("\nNo negative durations found with current parsing.")
        
    print("\nColumn Headers:", df.columns.tolist())

except Exception as e:
    print(f"Error: {e}")
