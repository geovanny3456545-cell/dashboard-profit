import yfinance as yf
import pandas as pd
import datetime

def diagnostic():
    # Sample trade from the user's data (WINJ26 @ 27/02/2026 10:57:12)
    trade_dt = datetime.datetime(2026, 2, 27, 10, 57, 12)
    sym = "^BVSP"
    
    print(f"--- Diagnóstico para {sym} ---")
    print(f"Horário do Trade (Planilha): {trade_dt}")
    
    # Fetch 2 days of data to be safe
    start = trade_dt - datetime.timedelta(days=1)
    end = trade_dt + datetime.timedelta(days=1)
    
    try:
        df = yf.download(sym, start=start, end=end, interval='5m', progress=False)
        if df.empty:
            print("ERRO: yfinance retornou DataFrame vazio.")
            return

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [str(c[0]) for c in df.columns]

        print(f"\nDados obtidos: {len(df)} linhas")
        print(f"Primeiro registro: {df.index[0]}")
        print(f"Último registro: {df.index[-1]}")
        
        # Check TZ
        tz = df.index.tz
        print(f"Timezone detectado: {tz}")
        
        # Test slicing with original logic
        working_index = df.index.tz_localize(None) if tz is not None else df.index
        
        start_range = trade_dt - datetime.timedelta(hours=1)
        end_range = trade_dt + datetime.timedelta(hours=1)
        
        slice_df = df[ (working_index >= start_range) & (working_index <= end_range) ]
        
        print(f"\nFatiamento (1h antes/depois): {len(slice_df)} linhas encontradas")
        
        if len(slice_df) == 0:
            print("\n🚨 NENHUM DADO ENCONTRADO NO INTERVALO!")
            print("Buscando registros próximos para detectar o offset real...")
            # Find closest to trade_dt
            all_diffs = (working_index - trade_dt).total_seconds() / 3600
            min_diff_idx = abs(all_diffs).argmin()
            closest_dt = working_index[min_diff_idx]
            offset_hours = all_diffs[min_diff_idx]
            print(f"Registro mais próximo no Yahoo: {closest_dt}")
            print(f"Diferença real: {offset_hours:.2f} horas")
            
    except Exception as e:
        print(f"Erro no diagnóstico: {str(e)}")

if __name__ == "__main__":
    diagnostic()
