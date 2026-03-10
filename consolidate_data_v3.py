import pandas as pd
import io
import os

base_dir = r"g:\Meu Drive\Antigravity\Finançals Analysis (1)"
input_csv = os.path.join(base_dir, "trading_data_day_trade.csv")

def clean_currency(val):
    if pd.isna(val) or val == '': return 0.0
    val_str = str(val).strip().replace('"', '').replace("'", '').replace('R$', '').replace(' ', '')
    if not val_str: return 0.0
    if ',' in val_str and '.' in val_str:
        if val_str.find('.') < val_str.find(','): val_str = val_str.replace('.', '').replace(',', '.')
        else: val_str = val_str.replace(',', '')
    elif ',' in val_str: val_str = val_str.replace(',', '.')
    try: return float(val_str)
    except: return 0.0

def parse_date_robust(val):
    if pd.isna(val): return pd.NaT
    s = str(val).strip().replace('"', '').replace("'", "").replace('//', '/')
    if not s: return pd.NaT
    
    # Try direct parse
    dt = pd.to_datetime(s, dayfirst=True, errors='coerce')
    if not pd.isna(dt):
        # Heuristic for typos
        if dt.year == 2026 and dt.month > 3:
            if dt.month == dt.day: return pd.Timestamp(year=2026, month=3, day=dt.day, hour=dt.hour, minute=dt.minute)
            if dt.day == 6 and dt.month == 5: return pd.Timestamp(year=2026, month=3, day=6, hour=dt.hour, minute=dt.minute)
        return dt
        
    # Try split by ;
    if ';' in s:
        parts = s.split(';')
        for p in parts:
            d = pd.to_datetime(p, dayfirst=True, errors='coerce')
            if not pd.isna(d):
                t = next((x for x in parts if ':' in x), "00:00:00")
                return pd.to_datetime(f"{p} {t}", dayfirst=True, errors='coerce')
    return pd.NaT

with open(input_csv, 'r', encoding='utf-8') as f:
    lines = f.readlines()

headers = [h.strip().replace('"', '') for h in lines[0].strip().split(',')]

data_rows = []
for idx, line in enumerate(lines[1:]):
    line = line.strip()
    if not line: continue
    
    # CASE 1: Messy line with many semicolons
    if line.count(';') > 5:
        parts = [p.strip().replace('"', '') for p in line.replace(',', ';').split(';')]
        parts = [p for p in parts if p]
        if len(parts) >= 8:
            ativo = parts[0]
            dt = parse_date_robust(";".join(parts[:5]))
            # Result is often the first negative or the last currency-like string before the end
            res_val = 0.0
            for p in parts[8:]:
                v = clean_currency(p)
                if v != 0: res_val = v # Keep taking the latest one found
            
            data_rows.append({
                'Ativo': ativo, 'Abertura_Str': line[:50], 'Res. Bruto': str(res_val),
                'SETUP Operado': 'Consolidado (Messy)', 'Abertura_Date_Parsed': dt, 'Idx': idx
            })
    else:
        # CASE 2: Standard or partially filled CSV
        try:
            df_temp = pd.read_csv(io.StringIO(line), header=None)
            row = df_temp.iloc[0].tolist()
            if len(row) > 0:
                ativo = str(row[0])
                abertura = str(row[1]) if len(row) > 1 else ""
                result = str(row[6]) if len(row) > 6 else ("0" if len(row) < 7 else str(row[6]))
                setup = str(row[8]) if len(row) > 8 else "Unknown"
                dt = parse_date_robust(abertura)
                
                data_rows.append({
                    'Ativo': ativo, 'Abertura_Str': abertura, 'Res. Bruto': result,
                    'SETUP Operado': setup, 'Abertura_Date_Parsed': dt, 'Idx': idx
                })
        except: continue

df = pd.DataFrame(data_rows)
df['Res_Numeric'] = df['Res. Bruto'].apply(clean_currency)

start = pd.to_datetime('2026-03-02')
end = pd.to_datetime('2026-03-07')
week_df = df[(df['Abertura_Date_Parsed'] >= start) & (df['Abertura_Date_Parsed'] < end)].copy()

print(f"Total operations: {len(week_df)}")
print(f"Total profit: R$ {week_df['Res_Numeric'].sum():.2f}")
print("\nEntries:")
print(week_df[['Ativo', 'Abertura_Date_Parsed', 'Res_Numeric', 'SETUP Operado', 'Idx']].to_string())

week_df.to_csv("week_data_v3.csv", index=False)
