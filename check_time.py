
import pandas as pd
import sys

try:
    # Read manually skipping Bad lines to matches dashboard logic
    # The dashboard uses 'header_row_found' logic. 
    # But usually 'consolidado_raw.csv' has headers at line 5 (index 4) based on 'select -first 15'
    # Line 1: Conta...
    # Line 2: Titular...
    # Line 3: Data Inicial...
    # Line 4: Data Final...
    # Line 5: ,,,, (Empty?)
    # Line 6: WING26... (Data?) 
    # Wait, where is the Header? 
    # In the `type` output (Step 833), I don't see a Header row like "Ativo;Abertura..."
    # I see the data starts directly?
    # WING26;19/01/2026,09:59:42...
    # Maybe the Metadata IS the header in some weird way, or Header is missing?
    # If Header is missing, `dashboard.py` logic might default to hardcoded? 
    # No, `dashboard.py` scans for "Ativo" and "Abertura" (Line 109).
    # IF it doesn't find them, it yields empty df? 
    # Check Step 833 output again. 
    # The output shows lines 0-4 (Metadata) then Line 5 is empty, then Line 6 is WING26.
    # PROBABLY NO HEADER ROW in this file view?
    # Or maybe `consolidado_raw.csv` is just data?
    # But `dashboard.py` relies on finding "Abertura".
    # I'll check if there's any line with "Abertura" in the file.
    pass

    with open(r'g:\Meu Drive\Antigravity\Finançals Analysis\consolidado_raw.csv', 'r', encoding='latin1') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        if 'Abertura' in line:
            print(f"Header found at line {i}: {line.strip()}")
            break
            
    # Check for times > 12:00 manually in col 1 (index 1) which is "19/01/2026,10:09:26"
    count_tarde = 0
    for line in lines:
        if ';' in line:
            parts = line.split(';')
            if len(parts) > 2:
                # col 1: 19/01/2026,09:59:42
                ts = parts[1]
                if ',' in ts:
                    time_part = ts.split(',')[1]
                    # time_part like 09:59:42
                    if ':' in time_part:
                        h = int(time_part.split(':')[0])
                        if h >= 12:
                            count_tarde += 1
                            if count_tarde < 5: print(f"Tarde trade: {ts}")
                            
    print(f"Total trades declared as Tarde: {count_tarde}")

except Exception as e:
    print(e)
