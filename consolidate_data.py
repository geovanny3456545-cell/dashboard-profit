import pandas as pd
import io
import re
import os

base_dir = r"g:\Meu Drive\Antigravity\Finançals Analysis (1)"
input_csv = os.path.join(base_dir, "trading_data_day_trade.csv")

def clean_currency(val):
    if pd.isna(val) or val == '': return 0.0
    val_str = str(val).strip().replace('R$', '').replace(' ', '')
    if ',' in val_str and '.' in val_str: val_str = val_str.replace('.', '').replace(',', '.')
    elif ',' in val_str: val_str = val_str.replace(',', '.')
    try: return float(val_str)
    except: return 0.0

def parse_date_with_time(val):
    if pd.isna(val): return pd.NaT
    s = str(val).strip()
    try:
        if ';' in s:
            # Handle HH:MM:SS;DD/MM/YYYY
            parts = s.split(';')
            if len(parts) >= 2:
                time_part = parts[0]
                date_part = parts[1]
                return pd.to_datetime(f"{date_part} {time_part}", dayfirst=True)
        # Handle regular formats
        return pd.to_datetime(s, dayfirst=True)
    except:
        return pd.NaT

def solve_messy_line(line, expected_cols):
    # Try to split by either , or ; but respect quotes
    # This is a bit complex for a regex, so let's simplify:
    # Most messy lines have a lot of ; and some ,
    # Replace all ; with , and then try to parse as CSV
    cleaned = line.replace(';', ',')
    # Use io.StringIO and pd.read_csv to handle quotes correctly
    df_temp = pd.read_csv(io.StringIO(cleaned), header=None)
    row = df_temp.iloc[0].tolist()
    
    # Filter out empty strings/NaNs at the end
    row = [r for r in row if pd.notna(r) and str(r).strip() != '']
    return row

# Read raw lines
with open(input_csv, 'r', encoding='utf-8') as f:
    lines = f.readlines()

headers = lines[0].strip().split(',')
# Clean headers
headers = [h.replace('\\n', ' ').replace('\n', ' ').strip() for h in headers]

data_rows = []
for line in lines[1:]:
    if not line.strip(): continue
    
    # Check if it's a messy line (contains many semicolons)
    if line.count(';') > 5:
        # Messy line detected
        # In the messy line example: WINJ26;06/03/2026,10:07:54;06/03/2026,...
        # It's better to just join everything with ; and split by ;
        line_clean = line.replace(',', ';')
        # Remove extra quotes that might be there
        line_clean = line_clean.replace('"', '')
        parts = [p.strip() for p in line_clean.split(';')]
        # Filter out empty parts
        parts = [p for p in parts if p]
        
        # Mapping for the messy format (based on observation)
        # Format seems to be: Ativo, Abertura_Date, Abertura_Time, Fechamento_Date, Fechamento_Time, Tempo, Qtd_Entrada, Qtd_Saida, Lado, ...
        # This is quite different. Let's try to extract what matters: Ativo, Abertura, Res. Bruto, Setup
        
        if len(parts) >= 15:
            ativo = parts[0]
            data_abertura = parts[1]
            hora_abertura = parts[2]
            abertura_full = f"{hora_abertura};{data_abertura}"
            
            # Res. Bruto is usually around index 12-14 in the split
            # Based on: WINJ26;06/03/2026;10:07:54;06/03/2026;10:15:14;7min19s;2;2;V;182.970,00;182.970,00;182.965,00;365,00;-35,00
            # Wait, 365.00 is Res. Bruto? No, -35.00?
            # Let's look at the "Stop vs Limit" logic too.
            
            # I'll use a more heuristic approach: look for currency-like strings
            res_bruto = "0"
            for p in parts[10:20]:
                if '-' in p or ',' in p:
                    if any(char.isdigit() for char in p):
                        res_bruto = p
                        # Keep looking for the last one that looks like a result?
            
            data_rows.append({
                'Ativo': ativo,
                'Abertura': abertura_full,
                'Res. Bruto': res_bruto,
                'Tipo de Ordem': 'Limit' if 'limite' in line.lower() else ('Stop' if 'stop' in line.lower() else 'Other'),
                'SETUP Operado': 'Consolidado/Messy',
                'Abertura_Date_Parsed': parse_date_with_time(abertura_full)
            })
    else:
        # Standard format
        parts = line.strip().split(',')
        if len(parts) >= len(headers):
            row_dict = dict(zip(headers, parts))
            row_dict['Abertura_Date_Parsed'] = parse_date_with_time(row_dict.get('Abertura'))
            data_rows.append(row_dict)

df_clean = pd.DataFrame(data_rows)
df_clean['Res_Numeric'] = df_clean['Res. Bruto'].apply(clean_currency)

# Filter for the week
start_date = pd.to_datetime('2026-03-02')
end_date = pd.to_datetime('2026-03-07') # Include Friday 06/03
week_df = df_clean[(df_clean['Abertura_Date_Parsed'] >= start_date) & (df_clean['Abertura_Date_Parsed'] < end_date)].copy()

print(f"Total operations in the week: {len(week_df)}")
print(f"Total profit: R$ {week_df['Res_Numeric'].sum():.2f}")
print("\nIndividual operations found:")
print(week_df[['Ativo', 'Abertura', 'Res. Bruto', 'Res_Numeric', 'SETUP Operado']])

# Save cleaned week data for later report generation
week_df.to_csv("week_data_cleaned.csv", index=False)
