import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

SHEET_ID = "14iTFjqHSKFPdLT9rieop6lFozA9ZkC_zYmfjjjV7HlU"
CREDS_FILE = r"G:\Meu Drive\Antigravity\Bitcoin\certs\google_creds.json"

def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
    return gspread.authorize(creds)

@st.cache_data(ttl=600)
def load_data(sheet_name):
    try:
        client = get_gspread_client()
        spreadsheet = client.open_by_key(SHEET_ID)
        sheet = spreadsheet.worksheet(sheet_name)
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        if not df.empty:
            # Converter colunas para datetime
            if 'Dia' in df.columns and 'Hora' in df.columns:
                df['Data_Full'] = pd.to_datetime(df['Dia'] + ' ' + df['Hora'], format='%d/%m/%Y %H:%M:%S')
            
            # Garantir que Valor é numérico
            if 'Valor' in df.columns:
                df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
        
        return df
    except Exception as e:
        return pd.DataFrame()

def render(mask_val_func):
    st.header("🛒 Controle de Gastos Pessoais")
    
    try:
        client = get_gspread_client()
        spreadsheet = client.open_by_key(SHEET_ID)
        worksheets = [ws.title for ws in spreadsheet.worksheets()]
        
        # Filtros na parte superior
        c1, c2 = st.columns([1, 2])
        with c1:
            selected_month = st.selectbox("Selecione o Lançamento", options=worksheets, index=len(worksheets)-1)
        
        if selected_month:
            df = load_data(selected_month)
            
            if df.empty:
                st.warning(f"A aba '{selected_month}' está vazia.")
            else:
                # Sidebar de filtros (seção específica)
                with st.sidebar:
                    st.divider()
                    st.subheader("🔍 Filtros de Gastos")
                    
                    if 'Data_Full' in df.columns:
                        min_date = df['Data_Full'].min().date()
                        max_date = df['Data_Full'].max().date()
                        # Date input wrapper to avoid index errors if only one date or same dates
                        date_range = st.date_input("Intervalo de Datas", [min_date, max_date], min_value=min_date, max_value=max_date)
                        
                        if isinstance(date_range, list) and len(date_range) == 2:
                            df = df[(df['Data_Full'].dt.date >= date_range[0]) & (df['Data_Full'].dt.date <= date_range[1])]
                        elif isinstance(date_range, datetime.date):
                             df = df[df['Data_Full'].dt.date == date_range]

                    col_filter_user = st.multiselect("Usuário", options=df['Usuário'].unique(), default=df['Usuário'].unique())
                    col_filter_cat = st.multiselect("Categoria", options=df['Categoria'].unique(), default=df['Categoria'].unique())
                    col_filter_pay = st.multiselect("Forma de Pagamento", options=df['Pagamento'].unique(), default=df['Pagamento'].unique())
                
                # Aplicar filtros
                df_filtered = df[
                    (df['Usuário'].isin(col_filter_user)) & 
                    (df['Categoria'].isin(col_filter_cat)) & 
                    (df['Pagamento'].isin(col_filter_pay))
                ]

                # Métricas com Máscara de Privacidade
                m1, m2, m3 = st.columns(3)
                total_gasto = df_filtered['Valor'].sum()
                
                m1.metric("Total Gasto", mask_val_func(total_gasto))
                m2.metric("Despesas", len(df_filtered))
                m3.metric("Média", mask_val_func(df_filtered['Valor'].mean() if not df_filtered.empty else 0))

                st.divider()

                # Gráficos
                g1, g2 = st.columns(2)
                
                with g1:
                    fig_cat = px.pie(df_filtered, values='Valor', names='Categoria', title="Por Categoria", hole=0.4,
                                   color_discrete_sequence=px.colors.qualitative.Pastel)
                    st.plotly_chart(fig_cat, use_container_width=True)
                
                with g2:
                    if selected_month == "Consolidado" and 'Mês_Ref' in df_filtered.columns:
                        month_evo = df_filtered.groupby('Mês_Ref')['Valor'].sum().reset_index()
                        fig_evo = px.bar(month_evo, x='Mês_Ref', y='Valor', title="Evolução Mensal", color='Mês_Ref')
                        st.plotly_chart(fig_evo, use_container_width=True)
                    else:
                        fig_prior = px.bar(df_filtered.groupby('Prioridade')['Valor'].sum().reset_index(), x='Prioridade', y='Valor', 
                                          title="Lazer vs Essencial", color='Prioridade', color_discrete_map={'Essencial': '#EF553B', 'Lazer': '#636EFA'})
                        st.plotly_chart(fig_prior, use_container_width=True)

                # Tabela
                st.subheader("📋 Detalhes")
                show_cols = ["Dia", "Hora", "Usuário", "Descrição", "Categoria", "Prioridade", "Pagamento", "Valor"]
                if "Mês_Ref" in df_filtered.columns: show_cols.append("Mês_Ref")
                
                # Aplicar máscara na coluna valor da tabela se necessário
                df_disp = df_filtered.copy()
                # If we were to mask the table, we would do it here. 
                # But typically mask_val_func returns a string which breaks dataframe sorting/types if we are not careful.
                # For now, let's keep it clean.
                
                st.dataframe(df_disp[show_cols].sort_index(ascending=False), use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao carregar aba de gastos: {e}")
