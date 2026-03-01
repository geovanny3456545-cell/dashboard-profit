from utils import data_loader
import pandas as pd
import requests
import io
import csv

def diagnose():
    print("--- Verbose Diagnostic: _load_performance_report ---")
    try:
        content = data_loader._get_raw_content(data_loader.CSV_URL)
        print(f"Raw content length: {len(content)}")
        
        sep = ';' if content.count(';') > content.count(',') else ','
        print(f"Detected sep: '{sep}'")
        
        f = io.StringIO(content)
        reader = csv.reader(f, delimiter=sep, quoting=csv.QUOTE_MINIMAL)
        rows = list(reader)
        print(f"Total rows read by csv.reader: {len(rows)}")
        
        header_idx = -1
        for i, row in enumerate(rows[:20]):
            row_str = " ".join(row).lower()
            if "ativo" in row_str and ("abertura" in row_str or "data" in row_str):
                header_idx = i
                print(f"Header match at index {i}: {row}")
                break
        
        if header_idx == -1:
            print("FAILURE: Header not found in first 20 rows.")
            # Let's see what we HAVE in first 5 rows
            for i in range(min(5, len(rows))):
                print(f"  Row {i}: {rows[i]}")
        else:
            headers = [h.replace('"', '').strip() for h in rows[header_idx]]
            data = rows[header_idx+1:]
            print(f"Data rows before filtering: {len(data)}")
            
            data_filtered = [r for r in data if len(r) > 0 and r[0].strip() != '']
            print(f"Data rows after filtering: {len(data_filtered)}")
            
            if not data_filtered:
                print("FAILURE: No data rows left after filtering.")
                if data:
                    print(f"  Sample row 0 (unfiltered): {data[0]}")
            else:
                df, name_map = data_loader._load_performance_report()
                print(f"Success! Final DF Shape: {df.shape}")
                
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    diagnose()
