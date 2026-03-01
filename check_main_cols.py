from utils import data_loader
import pandas as pd

def check_cols():
    df, name_map = data_loader.load_data()
    print("Columns in Main DF:")
    print(df.columns.tolist())
    print("\nName Map:")
    print(name_map)

if __name__ == "__main__":
    check_cols()
