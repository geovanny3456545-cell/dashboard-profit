import os

base_dir = r"g:\Meu Drive\Antigravity\Finançals Analysis"
raw_path = os.path.join(base_dir, "consolidado_raw.csv")

try:
    with open(raw_path, 'r', encoding='utf-8', errors='replace') as f:
        for i in range(10):
            print(f"Line {i}: {f.readline().strip()}")
except Exception as e:
    print(f"Error: {e}")
