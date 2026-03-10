import pandas as pd
import os
import re

base_dir = r"g:\Meu Drive\Antigravity\Finançals Analysis (1)"
raw_path = os.path.join(base_dir, "consolidado_raw.csv")
output_path = os.path.join(base_dir, "clean_consolidado.csv")

# Target Columns
columns = ['Ativo', 'Abertura', 'Fechamento', 'Tempo', 'Qtd', 'Lado', 'Res. Bruto']
rows = []

try:
    with open(raw_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
        
    for i in range(6, len(lines)):
        line = lines[i].strip()
        if not line or line.startswith(','): continue
        parts = line.split(';')
        if len(parts) < 3: continue
        
        ativo = parts[0]
        # Clean '15/01/2026,09:13:18' -> '15/01/2026 09:13:18'
        abertura = parts[1].replace(',', ' ') 
        fechamento_date = parts[2]
        
        # Regex to find quoted content
        match = re.search(r'"(.*?)"', line)
        if not match: continue
        
        quoted = match.group(1).split(';')
        if len(quoted) < 17: continue

        # Extract fields from quoted block
        fechamento_time = quoted[0]
        tempo = quoted[1]
        qtd = quoted[2]
        lado = quoted[4]
        # Index 16 expected to be pure profit based on sample inspection
        # "600,00" in sample was index 16 of inner parts
        res = quoted[16]
        
        rows.append([ativo, abertura, f"{fechamento_date} {fechamento_time}", tempo, qtd, lado, res])
        
    df = pd.DataFrame(rows, columns=columns)
    df.to_csv(output_path, index=False, sep=';', encoding='utf-8-sig')
    print(f"Success. Rows: {len(df)}")
    print(df.head())
    
except Exception as e:
    print(e)
