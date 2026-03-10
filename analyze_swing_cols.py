import pandas as pd
import requests
import io

# SWING_URL from the previous steps
SWING_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=1798886578&single=true&output=csv"

def analyze_swing_cols():
    try:
        r = requests.get(SWING_URL)
        df = pd.read_csv(io.StringIO(r.text))
        print("Swing Trade Sheet Columns:")
        print(df.columns.tolist())
        print("\nFirst 3 rows (Columns I and J):")
        # Column I is index 8, J is index 9
        cols_to_show = df.columns[8:10] if len(df.columns) > 9 else df.columns[8:]
        print(df[cols_to_show].head(3))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_swing_cols()
