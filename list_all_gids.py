import requests
import re

SHEET_ID = "2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz"
URL = f"https://docs.google.com/spreadsheets/d/e/{SHEET_ID}/pubhtml"

try:
    print(f"Fetching {URL}...")
    response = requests.get(URL)
    response.raise_for_status()
    html = response.text
    
    print("\nSearching for sheet names and GIDs...")
    
    # Pattern usually found in the JSON config within the script tag
    matches = re.findall(r'name: "([^"]+)",\s*gid: "(\d+)"', html)
    if matches:
        print(f"Found {len(matches)} sheets:")
        for name, gid in matches:
            print(f"Sheet: '{name}' -> GID: {gid}")
    else:
        print("No matches found with standard regex.")
        # Fallback to search for any link with gid=
        links = re.findall(r'gid=(\d+)', html)
        print(f"Found {len(links)} GIDs in links: {set(links)}")
        
except Exception as e:
    print(f"Error: {e}")
