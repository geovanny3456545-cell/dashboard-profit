from utils import data_loader
import pandas as pd

def debug_loading():
    print("Testing _load_performance_report...")
    try:
        df, name_map = data_loader._load_performance_report()
        print(f"Report loaded. Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        print(f"Name Map: {name_map}")
        
        if not df.empty:
            print(f"Sample Qtd_Clean: {df['Qtd_Clean'].head().tolist()}")
            if 'Abertura_Dt' in df.columns:
                print(f"Sample Dates: {df['Abertura_Dt'].head().tolist()}")
    except Exception as e:
        print(f"Error in _load_performance_report: {e}")
        import traceback
        traceback.print_exc()

    print("\nTesting load_data (with patterns)...")
    try:
        df, name_map = data_loader.load_data()
        print(f"Full data loaded. Shape: {df.shape}")
        if 'Pattern' in df.columns:
            print(f"Pattern counts:\n{df['Pattern'].value_counts().head()}")
    except Exception as e:
        print(f"Error in load_data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_loading()
