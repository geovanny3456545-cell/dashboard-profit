import streamlit as st
import pandas as pd
import datetime

# --- Modules ---
from utils import data_loader
from utils import metrics as m
from tabs import resumo, operacoes, graficos, calendario, ativos, relatorio, mentoria, swing, opcoes

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Relatório de Performance - ProfitPro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- AUTHENTICATION ---
def check_password():
    """Returns True if the user had the correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets.get("PASSWORD", "admin123"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Digite a senha de acesso ao Dashboard", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Senha incorreta. Digite novamente", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Senha incorreta.")
        return False
    else:
        # Password correct.
        return True

if not check_password():
    st.stop()

# --- CSS STYLING ---
st.markdown("""
<style>
    /* Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #2b2b2b;
        border: 1px solid #3e3e3e;
        padding: 10px;
        border-radius: 4px;
        color: white;
    }
    div[data-testid="metric-container"] label { font-size: 0.8em; color: #aaa; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { font-size: 1.2em; font-weight: bold; }
    
    /* ProfitPro Specific Colors */
    .profit-val { color: #00fa9a; font-weight: bold; }
    .loss-val { color: #ff4d4d; font-weight: bold; }
    .neutral-val { color: #bbbbbb; font-weight: bold; }
    
    /* Calendar Modern */
    .cal-container { font-family: 'Segoe UI', sans-serif; background-color: #1e1e1e; border: 1px solid #333; border-radius: 4px; padding: 10px; }
    .cal-header { 
        background-color: #111; 
        color: #fff; 
        font-weight: bold; 
        text-align: center; 
        padding: 10px;
        border-bottom: 2px solid #333;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .cal-table { width: 100%; border-collapse: separate; border-spacing: 2px; }
    .cal-cell {
        background-color: #252525;
        border-radius: 4px;
        vertical-align: top;
        padding: 5px;
        height: 80px;
        width: 14.28%;
        position: relative;
    }
    .cal-cell:hover { background-color: #333; }
    .day-num { font-size: 0.9em; color: #888; margin-bottom: 5px; text-align: right; }
    .day-val { font-size: 0.85em; font-weight: bold; text-align: center; margin-top: 5px; display: block; }
    .val-pos { color: #00fa9a; }
    .val-neg { color: #ff4d4d; }
    .note-indicator { 
        position: absolute; bottom: 5px; right: 5px; 
        width: 6px; height: 6px; background-color: #ea4335; border-radius: 50%; 
    }
    
    /* Grid Layout */
    .grid-row { display: flex; justify-content: space-between; border-bottom: 1px solid #444; padding: 8px 0; font-size: 0.9em; }
    .grid-label { color: #aaa; }
    .grid-value { font-weight: bold; text-align: right; }
    .grid-header { font-size: 1.1em; font-weight: bold; margin-bottom: 10px; color: #00aaff; border-bottom: 2px solid #00aaff; padding-bottom: 5px; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; border-bottom: 1px solid #444; }
    .stTabs [data-baseweb="tab"] { height: 40px; white-space: pre-wrap; background-color: transparent; border: none; color: #aaa; font-size: 0.9em; }
    .stTabs [aria-selected="true"] { background-color: transparent; color: #fff; border-bottom: 2px solid #00aaff; font-weight: bold; }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #1e1e1e; }
    ::-webkit-scrollbar-thumb { background: #444; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #555; }
</style>
""", unsafe_allow_html=True)

# Sidebar: Refresh Button
with st.sidebar:
    st.markdown("### Configurações")
    if st.button("🔄 Recarregar Dados"):
        st.cache_data.clear()
        # Full session state clear to be 100% sure
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    if 'last_refresh' in st.session_state:
        st.caption(f"Última atualização: {st.session_state['last_refresh']}")
    
    # Debug Expander for data verification
    st.markdown("---")
    st.caption(f"🚀 **Versão:** `2.3.2-stable` | **Sync:** ✅")
    
    if 'df_raw' in st.session_state and not st.session_state['df_raw'].empty:
        with st.sidebar.expander("🔍 Debug de Sincronização"):
            df = st.session_state['df_raw']
            st.write("**Padrões encontrados na planilha:**")
            pats = df['RealPattern_View'].unique().tolist()
            for p in sorted(pats):
                st.write(f"- {p}")
            st.info("Se você deletou um nome na planilha e ele ainda aparece aqui, verifique se a coluna 'Setup Real' também foi limpa.")

# --- LOAD DATA (Session State Caching) ---
if 'df_raw' not in st.session_state:
    with st.spinner("Carregando dados..."):
        try:
            st.session_state['df_raw'], st.session_state['col_map'] = data_loader.load_data()
            st.session_state['df_swing'] = data_loader.load_swing_trade_data()
            st.session_state['last_refresh'] = datetime.datetime.now().strftime("%H:%M:%S")
        except Exception as e:
            st.error(f"Erro no carregamento: {e}")
            st.stop()

df_raw = st.session_state['df_raw']
col_map = st.session_state['col_map']

if df_raw.empty:
    st.error("Erro ao carregar os dados. Verifique a conexão ou a URL do Google Sheets.")
    st.stop()

# --- TOP BAR FILTERS ---
c_filter1, c_filter2, c_filter3, c_spacer = st.columns([1.5, 1.5, 2, 6])

with c_filter1:
    ativo_col = col_map.get('Ativo', 'Ativo')
    if ativo_col in df_raw.columns:
        assets = sorted(df_raw[ativo_col].astype(str).unique())
        selected_asset = st.selectbox("Ativo", ["Todos"] + assets)
    else:
        selected_asset = "Todos"

with c_filter2:
    period_options = ["Hoje", "Esta Semana", "Este Mês", "Semana Passada", "Mês Passado", "2026", "Total", "Personalizado"]
    # Default to Total (index 6)
    selected_period = st.selectbox("Periodicidade", period_options, index=6) 

# Date Logic
today = datetime.date.today()
start_date = df_raw['Date'].min()
end_date = df_raw['Date'].max()

if selected_period == "Hoje":
    start_date = end_date = today
elif selected_period == "Esta Semana":
    start_date = today - datetime.timedelta(days=today.weekday()) # Monday
    end_date = today
elif selected_period == "Este Mês":
    start_date = today.replace(day=1)
    end_date = today
elif selected_period == "Semana Passada":
    end_date = today - datetime.timedelta(days=today.weekday() + 1)
    start_date = end_date - datetime.timedelta(days=6)
elif selected_period == "Mês Passado":
    end_date = today.replace(day=1) - datetime.timedelta(days=1)
    start_date = end_date.replace(day=1)
elif selected_period == "2026":
    start_date = datetime.date(2026, 1, 1)
    end_date = datetime.date(2026, 12, 31)
elif selected_period == "Personalizado":
    with c_filter3:
        d_range = st.date_input("Intervalo", [start_date, end_date])
        if len(d_range) == 2: start_date, end_date = d_range

st.caption(f"Filtro: {start_date.strftime('%d/%m/%Y')} até {end_date.strftime('%d/%m/%Y')} ({selected_period})")

# Filter DataFrame
mask = (df_raw['Date'] >= start_date) & (df_raw['Date'] <= end_date)
if selected_asset != "Todos" and ativo_col in df_raw.columns: 
    mask = mask & (df_raw[ativo_col] == selected_asset)
df = df_raw[mask].copy()

# Calculate Metrics for Shared Use
metrics = m.calculate_metrics(df)

# --- NAVIGATION ---
tab_options = ["🏠 Resumo", "📊 Swing Trade", "📢 Mentoria", "⚡ Day Trade", "📈 Gráficos", "🌍 Ativos", "📅 Calendário", "📝 Relatórios", "💎 Opções"]
if "selected_main_tab" not in st.session_state: 
    st.session_state.selected_main_tab = "🏠 Resumo"
else:
    # Migrate old names to names with emojis for compatibility
    mapping = {
        "Resumo": "🏠 Resumo",
        "Mentoria": "📢 Mentoria",
        "Operações": "⚡ Day Trade",
        "Day Trade": "⚡ Day Trade",
        "Gráficos": "📈 Gráficos",
        "Ativos": "🌍 Ativos",
        "Calendário": "📅 Calendário",
        "Relatórios": "📝 Relatórios"
    }
    if st.session_state.selected_main_tab in mapping:
        st.session_state.selected_main_tab = mapping[st.session_state.selected_main_tab]

# Use radio for persistence
selected_main_tab = st.radio("Navegação Principal", tab_options, horizontal=True, label_visibility="collapsed", key="selected_main_tab")
st.markdown("---")

# --- RENDER TABS ---
if selected_main_tab == "🏠 Resumo":
    resumo.render(df, metrics)

elif selected_main_tab == "📊 Swing Trade":
    swing.render(st.session_state.get('df_swing', pd.DataFrame()))

elif selected_main_tab == "📢 Mentoria":
    mentoria.render()

elif selected_main_tab == "⚡ Day Trade":
    operacoes.render(df, metrics)

elif selected_main_tab == "📈 Gráficos":
    graficos.render(df, df_raw)

elif selected_main_tab == "🌍 Ativos":
    ativos.render(df)

elif selected_main_tab == "📅 Calendário":
    calendario.render(df_raw, selected_asset)

elif selected_main_tab == "📝 Relatórios":
    relatorio.render()

elif selected_main_tab == "💎 Opções":
    opcoes.render()
# --- REBUILD TRIGGER ---
# Last Sync: 2026-03-06 07:35 BRT
# Version: 2.2.1-stable
