import pandas as pd
from utils.data_loader import load_data
import streamlit as st

# Mock st.secrets
st.secrets = {
    "CSV_URL": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa/pub?output=csv"
}

def inspect_prices():
    df, _, _ = load_data()
    df_dt = df[df['Categoria'] == 'Day Trade'].sort_values('Abertura_Dt', ascending=False)
    
    print(f"--- Inspeção de Preços Day Trade (Top 3) ---")
    for idx, row in df_dt.head(3).iterrows():
        print(f"\nAtivo: {row['Ativo']} ({row['Abertura']})")
        print(f"Lado: {row['Lado']}")
        print(f"Preço Compra (Raw): {row.get('Preço Compra')}")
        print(f"Preço Venda (Raw): {row.get('Preço Venda')}")
        print(f"Preço Compra (Num): {row.get('Preço Compra Numeric')}")
        print(f"Preço Venda (Num): {row.get('Preço Venda Numeric')}")
        print(f"Resultado: {row['Res. Operação']}")

if __name__ == "__main__":
    inspect_prices()
