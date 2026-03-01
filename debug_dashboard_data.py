
import pandas as pd
import requests
import io
import csv

# Main Data
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=872600748&single=true&output=csv"
# Patterns (GID might be wrong or empty)
PATTERN_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=2017205813&single=true&output=csv"

def debug_main():
    print("--- DEBUGGING MAIN DATA (TRADES) ---")
    try:
        r = requests.get(CSV_URL)
        f = io.StringIO(r.text)
        reader = csv.reader(f, delimiter=';')
        rows = list(reader)
        if len(rows) > 0:
            print(f"Total Rows: {len(rows)}")
            print("First 20 rows:")
            for i, r in enumerate(rows[:20]):
                print(f"Row {i}: {r}")
            
            # Check for Times
            time_idx = -1
            for i, h in enumerate(rows[0]):
                if "Abertura" in h: time_idx = i
            
            if time_idx != -1:
                print(f"\nTime Column Index: {time_idx}")
                print("First 10 Time Values:")
                for i in range(1, 11):
                    if i < len(rows):
                        print(f"Row {i}: {rows[i][time_idx]}")
        else:
            print("Main Data Empty or too short.")
    except Exception as e:
        print(f"Error Main: {e}")

    print("\n--- DEBUGGING PATTERN DATA ---")
    try:
        r = requests.get(PATTERN_URL)
        print(f"Status Code: {r.status_code}")
        f = io.StringIO(r.text)
        reader = csv.reader(f, delimiter=';') # Trying ; first
        rows = list(reader)
        
        if len(rows) > 0:
            print("Headers found in Pattern Data:")
            print(rows[0])
            print(f"Total Rows: {len(rows)}")
            if len(rows) > 1:
                print("First Row of Pattern Data:")
                print(rows[1])
        else:
            print("Pattern Data seems empty.")

    except Exception as e:
        print(f"Error Pattern: {e}")

if __name__ == "__main__":
    debug_main()
