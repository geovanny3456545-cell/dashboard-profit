import requests
import re

SHEET_ID = "2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz"
URL = f"https://docs.google.com/spreadsheets/d/e/{SHEET_ID}/pubhtml"

try:
    print(f"Fetching {URL}...")
    response = requests.get(URL)
    response.raise_for_status()
    html = response.text
    
    # regex to find tab names and GIDs
    # Layout often: {name: "Sheet1", gid: "123"}
    # Or in the menu: <li id="sheet-menu-trigger">...</li>
    # The pubhtml usually has a script block with config.
    
    print("Searching for sheet names and GIDs...")
    
    matches = re.findall(r'name: "([^"]+)",\s*gid: "(\d+)"', html)
    if matches:
        for name, gid in matches:
            print(f"Sheet: '{name}' -> GID: {gid}")
    else:
        # Fallback: look for other patterns
        # Sometimes it's `gid` then `name`
        print("Regex 1 failed. Trying loose search...")
        # Just find distinct GIDs and check context
        gids = re.findall(r'gid=(\d+)', html)
        print(f"Found GIDs in links: {set(gids)}")
        
        # Look for the specific name
        if "Consolidado_Day_Trade" in html:
            print("Found 'Consolidado_Day_Trade' in HTML!")
        else:
            print("'Consolidado_Day_Trade' NOT found in HTML. Maybe it's not published?")

except Exception as e:
    print(f"Error: {e}")
