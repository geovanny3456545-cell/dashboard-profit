import requests

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=872600748&single=true&output=csv"
PATTERN_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=2017205813&single=true&output=csv"

def inspect():
    print("--- PERFORMANCE REPORT RAW ---")
    r1 = requests.get(CSV_URL)
    print(f"Status: {r1.status_code}")
    print("First 500 chars:")
    print(r1.text[:500])
    
    print("\n--- PATTERN SHEET RAW ---")
    r2 = requests.get(PATTERN_URL)
    print(f"Status: {r2.status_code}")
    print("First 500 chars:")
    print(r2.text[:500])

if __name__ == "__main__":
    inspect()
