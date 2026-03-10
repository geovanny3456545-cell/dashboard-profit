import pandas as pd
import io
import re
import os

base_dir = r"g:\Meu Drive\Antigravity\Finançals Analysis (1)"
input_csv = os.path.join(base_dir, "trading_data_day_trade.csv")

def clean_currency(val):
    if pd.isna(val) or val == '': return 0.0
    # Add cleaning for quotes and R$
    val_str = str(val).strip().replace('"', '').replace("'", '').replace('R$', '').replace(' ', '')
    if not val_str: return 0.0
    
    # Handle European format (1.000,00)
    if ',' in val_str and '.' in val_str:
        if val_str.find('.') < val_str.find(','): # 1.000,00
            val_str = val_str.replace('.', '').replace(',', '.')
        else: # 1,000.00
            val_str = val_str.replace(',', '')
    elif ',' in val_str: # 1000,00
        val_str = val_str.replace(',', '.')
    
    try: return float(val_str)
    except: return 0.0

def parse_date_robust(val):
    if pd.isna(val): return pd.NaT
    s = str(val).strip().replace('"', '')
    if not s: return pd.NaT
    
    # Handle 03/03//2026
    s = s.replace('//', '/')
    
    try:
        dt = pd.to_datetime(s, dayfirst=True, errors='coerce')
        if pd.isna(dt):
            # Try semicolon split
            if ';' in s:
                parts = s.split(';')
                if len(parts) >= 2:
                    # Check if date is in part 0 or 1
                    for p in parts:
                        temp = pd.to_datetime(p, dayfirst=True, errors='coerce')
                        if not pd.isna(temp):
                            # Try to combine with first time-like part
                            time_part = ""
                            for p2 in parts:
                                if ':' in p2: time_part = p2; break
                            return pd.to_datetime(f"{p} {time_part}", dayfirst=True)
        
        # HEURISTIC: If year is 2026 and month is > 3 and day is same as month (04/04, 05/05)
        # and we are in March 2026, it's probably a typo for March (04/03, 05/03)
        if not pd.isna(dt) and dt.year == 2026 and dt.month > 3:
            if dt.month == dt.day:
                # Likely typo: 04/04 -> 04/03
                return pd.Timestamp(year=2026, month=3, day=dt.day, hour=dt.hour, minute=dt.minute)
            elif dt.day == 6 and dt.month == 5: # 06/05 -> 06/03
                 return pd.Timestamp(year=2026, month=3, day=6, hour=dt.hour, minute=dt.minute)
                 
        return dt
    except:
        return pd.NaT

# Read raw lines
with open(input_csv, 'r', encoding='utf-8') as f:
    lines = f.readlines()

headers = lines[0].strip().split(',')
headers = [h.replace('\\n', ' ').replace('\n', ' ').strip().replace('"', '') for h in headers]

data_rows = []
for idx, line in enumerate(lines[1:]):
    if not line.strip(): continue
    
    if line.count(';') > 5:
        line_clean = line.replace('"', '').replace(',', ';')
        parts = [p.strip() for p in line_clean.split(';')]
        parts = [p for p in parts if p]
        
        if len(parts) >= 10:
            # Try to find Ativo
            ativo = parts[0]
            # Try to find Date
            dt_raw = ";".join(parts[:5]) # heuristic
            dt_parsed = parse_date_robust(dt_raw)
            
            # Find Result
            res_bruto = "0"
            for p in reversed(parts): # Result often at end of numerical block
                 val = clean_currency(p)
                 if val != 0:
                     res_bruto = p
                     break
            
            data_rows.append({
                'Ativo': ativo,
                'Abertura_Str': dt_raw,
                'Res. Bruto': res_bruto,
                'Tipo de Ordem': 'Limit' if 'limite' in line.lower() else ('Stop' if 'stop' in line.lower() else 'Other'),
                'SETUP Operado': 'Consolidado (Messy)',
                'Abertura_Date_Parsed': dt_parsed
            })
    else:
        # Standard CSV
        # Use pandas read_csv for a single line to be safe with quotes
        try:
            df_temp = pd.read_csv(io.StringIO(line), header=None)
            row = df_temp.iloc[0].tolist()
            if len(row) >= len(headers):
                row_dict = dict(zip(headers, row))
                row_dict['Abertura_Date_Parsed'] = parse_date_robust(row_dict.get('Abertura'))
                data_rows.append(row_dict)
        except:
            continue

df_clean = pd.DataFrame(data_rows)
df_clean['Res_Numeric'] = df_clean['Res. Bruto'].apply(clean_currency)

# Filter for the week
start_date = pd.to_datetime('2026-03-02')
end_date = pd.to_datetime('2026-03-07')
week_df = df_clean[(df_clean['Abertura_Date_Parsed'] >= start_date) & (df_clean['Abertura_Date_Parsed'] < end_date)].copy()

print(f"Total operations in the week: {len(week_df)}")
print(f"Total profit: R$ {week_df['Res_Numeric'].sum():.2f}")
print("\nIndividual operations found:")
print(week_df[['Ativo', 'Abertura_Date_Parsed', 'Res. Bruto', 'Res_Numeric', 'SETUP Operado']])

# Setup Breakdown
print("\n--- Setup Breakdown ---")
setups = week_df.groupby('SETUP Operado')['Res_Numeric'].sum().sort_values(ascending=False)
print(setups)

# Order Type Breakdown
print("\n--- Order Type Breakdown ---")
# Standardize order type
def std_order(row):
    val = str(row.get('Tipo de Ordem', '')).lower()
    setup = str(row.get('SETUP Operado', '')).lower()
    if 'limite' in val or 'limite' in setup: return 'Limit'
    if 'stop' in val or 'stop' in setup: return 'Stop'
    return 'Other'

week_df['Order_Type_Std'] = week_df.apply(std_order, axis=1)
order_stats = week_df.groupby('Order_Type_Std').agg(
    Qtd=('Res_Numeric', 'count'),
    Lucro=('Res_Numeric', 'sum')
)
print(order_stats)

week_df.to_csv("week_data_final.csv", index=False)
