import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

st.set_page_config(page_title="Dashboard de Gastos Exclusivo", page_icon="💰", layout="wide")

# Configurações do Google Sheets
SHEET_ID = "14iTFjqHSKFPdLT9rieop6lFozA9ZkC_zYmfjjjV7HlU"
CREDS_FILE = r"G:\Meu Drive\Antigravity\Bitcoin\certs\google_creds.json"

st.title("💰 Controle de Gastos & Planejamento")
st.markdown("Dashboard exclusivo alimentado pelo **Telegram Bot**")

@st.cache_resource
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
    return gspread.authorize(creds)

@st.cache_data(ttl=600)
def load_data(sheet_name):
    client = get_gspread_client()
    spreadsheet = client.open_by_key(SHEET_ID)
    try:
        sheet = spreadsheet.worksheet(sheet_name)
        data = sheet.get_all_records()
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        if 'Dia' in df.columns and 'Hora' in df.columns:
            df['Data_Full'] = pd.to_datetime(df['Dia'] + ' ' + df['Hora'], dayfirst=True, errors='coerce')
        if 'Valor' in df.columns:
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar a aba {sheet_name}: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def load_planning():
    try:
        client = get_gspread_client()
        spreadsheet = client.open_by_key(SHEET_ID)
        sheet = spreadsheet.worksheet("Planejamento")
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        if not df.empty:
            df['Gasto Máximo Mensal'] = pd.to_numeric(df['Gasto Máximo Mensal'], errors='coerce').fillna(0)
        return df
    except Exception:
        return pd.DataFrame()

# Interface Principal
try:
    client = get_gspread_client()
    spreadsheet = client.open_by_key(SHEET_ID)
    worksheets = [ws.title for ws in spreadsheet.worksheets()]
    
    st.sidebar.header("📅 Período")
    selected_month = st.sidebar.selectbox("Selecione o Mês", options=worksheets, index=len(worksheets)-1)
    
    if selected_month:
        df = load_data(selected_month)
        df_plan = load_planning()
        
        if df.empty:
            st.warning(f"Sem dados na aba '{selected_month}'.")
        else:
            # Filtros Sidebar
            st.sidebar.divider()
            st.sidebar.header("🔍 Filtros")
            col_filter_user = st.sidebar.multiselect("Usuário", options=df['Usuário'].unique(), default=df['Usuário'].unique())
            col_filter_cat = st.sidebar.multiselect("Categoria", options=df['Categoria'].unique(), default=df['Categoria'].unique())
            
            # Aplicar Filtros
            df_filtered = df[(df['Usuário'].isin(col_filter_user)) & (df['Categoria'].isin(col_filter_cat))]

            # Métricas de Orçamento
            m1, m2, m3 = st.columns(3)
            total_real = df_filtered['Valor'].sum()
            total_meta = 0
            if not df_plan.empty:
                total_meta = df_plan[df_plan['Categoria'].isin(col_filter_cat)]['Gasto Máximo Mensal'].sum()

            m1.metric("Realizado", f"R$ {total_real:,.2f}", 
                      delta=f"{((total_real/total_meta)-1)*100:.1f}% da meta" if total_meta > 0 else None, delta_color="inverse")
            m2.metric("Planejado (Meta)", f"R$ {total_meta:,.2f}")
            m3.metric("Saldo Disponível", f"R$ {total_meta - total_real:,.2f}" if total_meta > 0 else "N/A")

            st.divider()

            # Gráficos
            c1, c2 = st.columns(2)
            with c1:
                if not df_plan.empty:
                    real_by_cat = df_filtered.groupby('Categoria')['Valor'].sum().reset_index()
                    comp_df = pd.merge(df_plan, real_by_cat, on='Categoria', how='left').fillna(0)
                    comp_df = comp_df[comp_df['Categoria'].isin(col_filter_cat)]
                    plot_df = comp_df.melt(id_vars='Categoria', value_vars=['Gasto Máximo Mensal', 'Valor'], var_name='Tipo', value_name='Total')
                    plot_df['Tipo'] = plot_df['Tipo'].replace({'Gasto Máximo Mensal': 'Meta', 'Valor': 'Realizado'})
                    fig_comp = px.bar(plot_df, x='Categoria', y='Total', color='Tipo', barmode='group', title="Meta vs Realizado",
                                    color_discrete_map={'Meta': '#636EFA', 'Realizado': '#EF553B'})
                    st.plotly_chart(fig_comp, use_container_width=True)
            
            with c2:
                fig_cat = px.pie(df_filtered, values='Valor', names='Categoria', title="Divisão das Despesas", hole=0.4)
                st.plotly_chart(fig_cat, use_container_width=True)

            # Tabela
            st.subheader("📋 Detalhamento")
            st.dataframe(df_filtered.sort_index(ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Erro: {e}")
