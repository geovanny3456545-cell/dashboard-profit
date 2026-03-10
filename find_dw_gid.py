import requests
import re

URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pubhtml"

try:
    resp = requests.get(URL)
    resp.raise_for_status()
    html = resp.text
    
    # Search for D/W Consolidado
    target = "D/W Consolidado"
    if target in html:
        print(f"Found '{target}' in HTML!")
        # Try to find the GID associated with this tab
        # Usually tabs are in a list like <li id="sheet-button-872600748"><a href="#872600748">D/W Consolidado (Operacional)</a></li>
        match = re.search(r'id="sheet-button-(\d+)".*?>.*?'+re.escape(target), html, re.IGNORECASE | re.DOTALL)
        if match:
            print(f"Found GID: {match.group(1)}")
        else:
            # Try finding the #GID in href near the target
            # Find the position of the target
            pos = html.find(target)
            snippet = html[pos-200:pos+200]
            print(f"Snippet around '{target}':\n{snippet}")
            # Look for GID in the snippet
            gid_match = re.search(r'gid=(\d+)', snippet)
            if not gid_match:
                gid_match = re.search(r'#(\d+)', snippet)
            
            if gid_match:
                print(f"Potential GID from snippet: {gid_match.group(1)}")
    else:
        print(f"'{target}' NOT found in HTML.")
        # Print all tab-like names found
        tabs = re.findall(r'<a[^>]+>([^<]+)</a>', html)
        print(f"Available tab names found in links: {tabs}")

except Exception as e:
    print(f"Error: {e}")
