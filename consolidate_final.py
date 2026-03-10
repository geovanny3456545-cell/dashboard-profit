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

def parse_date_ultra_robust(val):
    if pd.isna(val) or str(val).strip() == "": return pd.NaT
    s = str(val).strip().replace('"', '').replace("'", "").replace('//', '/')
    
    # Check for direct match first
    dt = pd.to_datetime(s, dayfirst=True, errors='coerce')
    
    # If it failed, try to split by common separators
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
    
    # TYPO FIXES for the current week (March 2026)
    if dt.year == 2026:
        # Case: 04/04 -> 04/03
        if dt.month == dt.day and dt.month > 3:
            return pd.Timestamp(year=2026, month=3, day=dt.day, hour=dt.hour, minute=dt.minute)
        # Case: 06/05 -> 06/03
        if dt.day == 6 and dt.month == 5:
            return pd.Timestamp(year=2026, month=3, day=6, hour=dt.hour, minute=dt.minute)
        # Case: 03/03/2026 (correct but double check)
        if dt.month == 3: return dt
        # Case: 06/02/2026 -> Might be Feb or Jun. Let's assume dayfirst=True works unless it's clearly out of range.
        
    return dt

with open(input_csv, 'r', encoding='utf-8') as f:
    lines = f.readlines()

data_rows = []
for idx, line in enumerate(lines[1:]):
    line = line.strip()
    if not line: continue
    
    # Ativo is typically the first part
    # Abertura is second
    # Result is 7th in standard CSV or somewhere in the messy string
    
    parts_comma = [p.strip() for p in line.split(',')]
    parts_semi = [p.strip() for p in line.split(';')]
    
    # Use whichever split gives more meaningful parts
    parts = parts_semi if len(parts_semi) > len(parts_comma) else parts_comma
    parts = [p.replace('"', '') for p in parts]
    
    if len(parts) < 2: continue
    
    ativo = parts[0]
    # Check if Ativo looks like a ticker (e.g. WING26, WINJ26)
    if not any(t in ativo.upper() for t in ['WIN', 'WDO', 'IBOV', 'PETR', 'VALE']):
        # Maybe it's a messy line where Ativo is embedded
        if ';' in line:
            ativo = parts[0].split(';')[0]
    
    dt = parse_date_ultra_robust(" ".join(parts[:5]))
    if pd.isna(dt): continue
    
    # Try to find a result
    res_val = 0.0
    for p in reversed(parts):
        v = clean_currency(p)
        if v != 0 and abs(v) > 1: # Ignore tiny values that might be indices
            res_val = v
            break
            
    setup = "Unknown"
    for p in parts:
        lower_p = p.lower()
        if any(s in lower_p for s in ['lateralidade', 'rompimento', 'canal', 'estatística']):
            setup = p
            break
            
    data_rows.append({
        'Ativo': ativo,
        'Data': dt,
        'Resultado': res_val,
        'Setup': setup,
        'Original': line[:100]
    })

df = pd.DataFrame(data_rows)
# Final week filter
start = pd.to_datetime('2026-03-02')
end = pd.to_datetime('2026-03-07')
week_df = df[(df['Data'] >= start) & (df['Data'] < end)].copy()

print(f"Total Weekly Ops: {len(week_df)}")
print(f"Total Weekly Profit: R$ {week_df['Resultado'].sum():.2f}")
print("\nOperations:")
print(week_df[['Data', 'Ativo', 'Resultado', 'Setup']])

# Aggregates
print("\n--- Summary ---")
print(week_df.groupby('Setup')['Resultado'].agg(['count', 'sum']))

week_df.to_csv("weekly_final_summary.csv", index=False)
