import requests
import io
import pandas as pd
import streamlit as st

# CSV_URL for Day Trade (GID 0 usually)
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=0&single=true&output=csv"

def check_headers():
    r = requests.get(CSV_URL)
    content = r.text
    df = pd.read_csv(io.StringIO(content))
    print("CSV Headers:")
    print(df.columns.tolist())
    print("\nFirst row sample:")
    print(df.iloc[0].to_dict())

if __name__ == "__main__":
    check_headers()
