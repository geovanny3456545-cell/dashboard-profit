import re
import os

# Define absolute paths
base_dir = r"C:\Users\geova\.gemini\antigravity\brain\c4617042-0810-400d-b9e3-ef65db61df87"
debug_file = os.path.join(base_dir, "debug_page.html")

try:
    with open(debug_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    print(f"Read {len(content)} bytes from debug_page.html")
    
    # Search for "OPERAÇÕES_DAY_TRADE"
    term = "OPERAÇÕES_DAY_TRADE"
    indices = [m.start() for m in re.finditer(re.escape(term), content)]
    
    if not indices:
        print(f"Term '{term}' not found in file.")
    else:
        print(f"Found '{term}' at indices: {indices}")
        for idx in indices:
            start = max(0, idx - 1000)
            end = min(len(content), idx + 1000)
            context = content[start:end]
            print(f"\nContext around index {idx}:")
            print("-" * 40)
            # Find closest 'gid' pattern
            gids = re.findall(r'gid\D+(\d{8,})', context)
            if gids:
                print(f"Potential GIDs near '{term}': {gids}")
                
            # Also just print raw context
            print(context)
            print("-" * 40)

except Exception as e:
    print(f"Error: {e}")
