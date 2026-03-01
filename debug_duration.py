from utils import data_loader
import pandas as pd

def debug_durations():
    df, _ = data_loader.load_data()
    if df.empty:
        print("DF is empty")
        return
    
    print("Initial Columns:", df.columns.tolist())
    
    if 'Abertura_Dt' in df.columns and 'Fechamento_Dt' in df.columns:
        df['Minutos'] = (df['Fechamento_Dt'] - df['Abertura_Dt']).dt.total_seconds() / 60
        
        print("\nFirst 10 rows of Duration Analysis:")
        cols_to_show = ['Abertura', 'Fechamento']
        if 'Hora Fechamento' in df.columns: cols_to_show.append('Hora Fechamento')
        cols_to_show.extend(['Abertura_Dt', 'Fechamento_Dt', 'Minutos'])
        
        print(df[cols_to_show].head(10))
        
        print("\nStatistics for Minutos:")
        print(df['Minutos'].describe())
        
        print("\nAny Negative Minutos?")
        print(len(df[df['Minutos'] < 0]))
        
        print("\nAny NaN Minutos?")
        print(df['Minutos'].isna().sum())

if __name__ == "__main__":
    debug_durations()
