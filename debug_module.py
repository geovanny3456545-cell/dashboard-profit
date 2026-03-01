import sys
import os

# Add current dir to path
sys.path.append(os.getcwd())

try:
    from utils import data_loader
    print(f"File path of data_loader: {data_loader.__file__}")
    print(f"Attributes: {dir(data_loader)}")
    if hasattr(data_loader, 'load_swing_trade_data'):
        print("SUCCESS: load_swing_trade_data FOUND.")
    else:
        print("ERROR: load_swing_trade_data MISSING.")
        # Print file content to check what Python actually reads
        with open(data_loader.__file__, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"Last 10 lines of the file as read by Python:\n{''.join(lines[-10:])}")
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
