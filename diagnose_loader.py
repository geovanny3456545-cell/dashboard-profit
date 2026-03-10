from utils import data_loader
import pandas as pd

def diagnose():
    print("--- Final Diagnostic: data_loader.load_data() ---")
    df, col_map = data_loader.load_data()
    print(f"Final DF Shape: {df.shape}")
    if not df.empty:
        print(f"Columns: {df.columns.tolist()}")
        print(f"Res_Numeric Sum: {df['Res_Numeric'].sum()}")
        print("First row preview:")
        print(df.iloc[0])
    else:
        print("FAILURE: DataFrame is still empty.")

if __name__ == "__main__":
    diagnose()
