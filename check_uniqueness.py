from utils import data_loader
import pandas as pd

def check_uniqueness():
    print("--- Uniqueness Check: load_data() ---")
    df, col_map = data_loader.load_data()
    
    # Check Columns
    cols = df.columns.tolist()
    dupes = set([x for x in cols if cols.count(x) > 1])
    
    if dupes:
        print(f"FAILURE: Duplicate columns found: {dupes}")
        print(f"All Columns: {cols}")
    else:
        print("Success! All columns are unique.")
        
    # Check Index
    if not df.index.is_unique:
        print("FAILURE: Index is NOT unique.")
    else:
        print("Success! Index is unique.")

if __name__ == "__main__":
    check_uniqueness()
