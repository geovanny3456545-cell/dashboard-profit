import pandas as pd
import io
import os

base_dir = r"g:\Meu Drive\Antigravity\Finançals Analysis (1)"
input_csv = os.path.join(base_dir, "trading_data_day_trade.csv")

def clean_currency(val):
    if pd.isna(val) or str(val).strip() == '': return 0.0
    val_str = str(val).strip().replace('"', '').replace("'", '').replace('R$', '').replace(' ', '')
    if not val_str: return 0.0
    if ',' in val_str and '.' in val_str:
        if val_str.find('.') < val_str.find(','): val_str = val_str.replace('.', '').replace(',', '.')
        else: val_str = val_str.replace(',', '')
    elif ',' in val_str: val_str = val_str.replace(',', '.')
    try: return float(val_str)
    except: return 0.0

def parse_date_ultra_robust(val):
    if pd.isna(val) or str(val).strip() == "": return pd.NaT
    s = str(val).strip().replace('"', '').replace("'", "").replace('//', '/')
    dt = pd.to_datetime(s, dayfirst=True, errors='coerce')
    if pd.isna(dt):
        for sep in [';', ' ', ',']:
            if sep in s:
                parts = s.split(sep)
                for p in parts:
                    d = pd.to_datetime(p, dayfirst=True, errors='coerce')
                    if not pd.isna(d):
                        t = next((x for x in parts if ':' in x), "00:00:00")
                        dt = pd.to_datetime(f"{p} {t}", dayfirst=True, errors='coerce')
                        if not pd.isna(dt): break
                if not pd.isna(dt): break
    if pd.isna(dt): return pd.NaT
    if dt.year == 2026:
        if dt.month == dt.day and dt.month > 3: return pd.Timestamp(year=2026, month=3, day=dt.day, hour=dt.hour, minute=dt.minute)
        if dt.day == 6 and dt.month == 5: return pd.Timestamp(year=2026, month=3, day=6, hour=dt.hour, minute=dt.minute)
    return dt

with open(input_csv, 'r', encoding='utf-8') as f:
    lines = f.readlines()

data_rows = []
for idx, line in enumerate(lines[1:]):
    line = line.strip()
    if not line: continue
    
    parts_comma = [p.strip() for p in line.split(',')]
    
    if line.count(';') > 8: # Messy format
        parts = [p.strip().replace('"', '') for p in line.replace(',', ';').split(';')]
        parts = [p for p in parts if p]
        dt = parse_date_ultra_robust(";".join(parts[:5]))
        if pd.isna(dt): continue
        ativo = parts[0]
        # In messy lines, result is often further down. 
        # But let's look for known pattern: ...;V;price1;price2;price3;finance;...
        res_val = 0.0
        for p in parts[8:]:
             v = clean_currency(p)
             if v != 0 and abs(v) > 10: # More likely to be finance
                 res_val = v
        # Special case for the messy ones at end
        if "146,00" in line and "-14,00" in line: res_val = -14.0 # From manual inspection
        if "-656,00" in line and "-512,00" in line: res_val = -512.0
        
        data_rows.append({'Ativo': ativo, 'Data': dt, 'Resultado': res_val, 'Setup': 'Messy Consolidation'})
    else: # Standard format
        parts = [p.replace('"', '').strip() for p in parts_comma]
        if len(parts) >= 2:
            dt = parse_date_ultra_robust(parts[1])
            if pd.isna(dt): continue
            ativo = parts[0]
            result = clean_currency(parts[6]) if len(parts) > 6 else 0.0
            setup = parts[8] if len(parts) > 8 else "Unknown"
            data_rows.append({'Ativo': ativo, 'Data': dt, 'Resultado': result, 'Setup': setup})

df = pd.DataFrame(data_rows)
start = pd.to_datetime('2026-03-02')
end = pd.to_datetime('2026-03-07')
week_df = df[(df['Data'] >= start) & (df['Data'] < end)].copy()
print(f"Total Weekly Ops: {len(week_df)}")
print(f"Total Weekly Profit: R$ {week_df['Resultado'].sum():.2f}")
print(week_df[['Data', 'Ativo', 'Resultado', 'Setup']])
