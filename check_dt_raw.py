import requests

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=0&single=true&output=csv"

def check_raw():
    r = requests.get(CSV_URL)
    print("Raw Content (First 500 chars):")
    print(r.text[:500])

if __name__ == "__main__":
    check_raw()
