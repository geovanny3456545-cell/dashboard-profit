import pandas as pd
import numpy as np
import sys
import os

# Set relative paths
DIR = r"g:\Meu Drive\Antigravity\Finançals Analysis (1)"
sys.path.append(DIR)

from utils.data_loader import load_data

def diagnostic():
    print("--- Diagnostic: Data Classification ---")
    df, _ = load_data()
    
    if df.empty:
        print("Error: DataFrame is empty.")
        return
        
    total = len(df)
    unclassified = len(df[df['Pattern'] == "Não Classificado"])
    classified = total - unclassified
    rate = (classified / total * 100) if total > 0 else 0
    
    print(f"Total trades: {total}")
    print(f"Classified: {classified}")
    print(f"Unclassified: {unclassified}")
    print(f"Success Rate: {rate:.2f}%")
    
    if unclassified > 0:
        print("\nFirst 5 unclassified trades:")
        cols = ['Abertura', 'Ativo', 'Pattern']
        print(df[df['Pattern'] == "Não Classificado"][cols].head())

if __name__ == "__main__":
    diagnostic()
