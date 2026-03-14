import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import csv
import datetime
import yfinance as yf

# --- Constants & Config ---
# --- Constants & Config from Secrets ---
CSV_URL = st.secrets.get("CSV_URL")
if not CSV_URL:
    st.error("CSV_URL não configurado em st.secrets")
    st.stop()
    
PATTERN_URL = st.secrets.get("PATTERN_URL")
if not PATTERN_URL:
    st.error("PATTERN_URL não configurado em st.secrets")
    st.stop()

def load_data():
    """Main entry for unified data loading with multi-layer caching."""
    try:
        df, name_map = _load_performance_report()
        if df.empty:
            return pd.DataFrame(), {}
            
        df_p = _load_pattern_sheet()
        
        if not df_p.empty:
            # Vectorized Merge Keys
            def get_base_ativo(ser):
                return ser.astype(str).str.strip().str.upper().str.extract(r'^([A-Z]{3})')[0]

            df['Ativo_Base'] = get_base_ativo(df['Ativo'])
            df_p['Ativo_Base'] = get_base_ativo(df_p['Ativo'])
            
            # Robust Timestamp Rounding (Floor to minute)
            df['Merge_Dt'] = df['Abertura_Dt'].dt.floor('min')
            df_p['Merge_Dt'] = df_p['Abertura_Dt'].dt.floor('min')

            # Clean possible stale columns from performance report before merge
            for col in ['Pattern', 'RealPattern', 'Tipo de Ordem', 'Observation', 'Management', 'HandError', 'Pattern_View', 'RealPattern_View']:
                if col in df.columns:
                    df = df.drop(columns=[col])

            # Optimized Merge - Keep LAST entry from spreadsheet if duplicates exist
            cols_to_use = ['Ativo_Base', 'Merge_Dt', 'Pattern', 'RealPattern', 'Tipo de Ordem', 'Management', 'HandError']
            df_p_clean = df_p.drop_duplicates(subset=['Ativo_Base', 'Merge_Dt'], keep='last')
            
            df = df.merge(df_p_clean[cols_to_use], on=['Ativo_Base', 'Merge_Dt'], how='left')
            
            # Defaults
            df['Pattern'] = df['Pattern'].fillna("Não Classificado")
            df['RealPattern'] = df['RealPattern'].fillna(df['Pattern'])
            df['Tipo de Ordem'] = df['Tipo de Ordem'].fillna("Não Classificado")
            df['Management'] = df['Management'].fillna("Ok")
            df['HandError'] = df['HandError'].fillna("Sim") # Mão correta: Sim (default)
            
            df['Pattern_View'] = df['Pattern'].map(normalize_pattern)
            df['RealPattern_View'] = df['RealPattern'].map(normalize_pattern)
            
            # Standardized Brooks Grouping
            def get_group(val):
                v = str(val).lower()
                if 'rompimento' in v or 'estreito' in v: return 'BTC (Momentum)'
                if 'lateral' in v or 'range' in v: return 'TR (Lateral)'
                if 'amplo' in v: return 'BC (Canal Amplo)'
                return 'Outro'
            
            df['Group_Operado'] = df['Pattern'].map(get_group)
            df['Group_Real'] = df['RealPattern'].map(get_group)
            
            df = df.drop(columns=['Ativo_Base', 'Merge_Dt'])

        # FINAL SAFETY: Ensure unique index and columns for Streamlit/Styler
        df = df.loc[:, ~df.columns.duplicated()].reset_index(drop=True)
            
        return df, name_map
    except Exception:
        return pd.DataFrame(), {}

@st.cache_data(ttl=1)  # Minimal TTL for raw fetch to force updates
def _get_raw_content(url):
    # Aggressive Cache-Buster: unique timestamp + no-cache headers
    cb_url = f"{url}&t={datetime.datetime.now().timestamp()}"
    headers = {
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Expires": "0"
    }
    r = requests.get(cb_url, headers=headers)
    r.raise_for_status()
    r.encoding = 'utf-8'
    return r.text

@st.cache_data(ttl=1)  # Minimal TTL to allow cache-busting to work
def _load_performance_report():
    """Robust parser for ProfitPro CSV exports."""
    try:
        content = _get_raw_content(CSV_URL)
        if not content: return pd.DataFrame(), {}
        lines = content.splitlines()
        
        header_idx = -1
        sep = ';' 
        for i, line in enumerate(lines[:20]):
            l_low = line.lower()
            if "ativo" in l_low and ("abertura" in l_low or "data" in l_low):
                header_idx = i
                # Robust separator detection: prefer ; if it appears multiple times
                if line.count(';') >= 5:
                    sep = ';'
                else:
                    sep = ',' if line.count(',') > line.count(';') else ';'
                break
        
        if header_idx == -1: return pd.DataFrame(), {}
        
        f = io.StringIO(content)
        for _ in range(header_idx): f.readline()
        
        header_line = f.readline().strip()
        reader_h = csv.reader(io.StringIO(header_line), delimiter=sep)
        headers = next(reader_h)
        # Clean headers: remove quotes AND replace internal commas with spaces for mapping
        headers = [h.replace('"', '').replace(',', ' ').strip() for h in headers]
        
        reader_d = csv.reader(f, delimiter=sep, quoting=csv.QUOTE_MINIMAL)
        # We enforce length consistency here
        data = [r for r in reader_d if len(r) > 0 and r[0].strip() != '']
        
        if not data: return pd.DataFrame(), {}
        
        # Max column detection for alignment
        max_cols = max(len(r) for r in data)
        if len(headers) < max_cols:
             new_headers = []
             for h in headers:
                 # Check for the specific "Tempo Operação" field which often splits
                 if 'Tempo' in h and 'Opera' in h:
                     new_headers.extend(['Hora Fechamento', 'Tempo Operação'])
                 else:
                     new_headers.append(h)
             while len(new_headers) < max_cols:
                 new_headers.append(f"Extra_{len(new_headers)}")
             headers = new_headers

        safe_data = [r + [''] * (len(headers) - len(r)) for r in data]
        df = pd.DataFrame(safe_data, columns=headers[:len(safe_data[0])])
        df = df.map(lambda x: x.replace('"', '').strip() if isinstance(x, str) else x)

        # Mapping Essentials - More strict for Qtd to avoid duplicates
        name_map = {}
        found_qtd = False
        for c in df.columns:
            cl = c.lower().strip()
            # Standard mappings (handles spaces/commas in names via header cleaning above)
            if 'ativo' in cl and 'ag' not in cl: name_map[c] = 'Ativo'
            elif 'abertura' in cl: name_map[c] = 'Abertura'
            elif 'fechamento' in cl and 'hora' not in cl: name_map[c] = 'Fechamento'
            elif 'res' in cl and 'bruto' in cl: name_map[c] = 'Res. Intervalo Bruto'
            elif 'res' in cl and 'intervalo' in cl and '%' not in cl and 'Bruto' not in name_map.values(): 
                name_map[c] = 'Res. Intervalo Bruto'
            elif 'lado' in cl: name_map[c] = 'Lado'
            elif 'preço' in cl and 'compra' in cl: name_map[c] = 'Preço Compra'
            elif 'preço' in cl and 'venda' in cl: name_map[c] = 'Preço Venda'
            elif 'médio' in cl: name_map[c] = 'Médio'
            elif 'qtd' in cl and not found_qtd:
                name_map[c] = 'Qtd'
                found_qtd = True

        df = df.rename(columns=name_map)
        
        # Vectorized Parsing
        if 'Abertura' in df.columns:
            df['Abertura_Dt'] = pd.to_datetime(df['Abertura'].str.replace(',', ' ', regex=False), dayfirst=True, errors='coerce')
            df['Date'] = df['Abertura_Dt'].dt.date
        
        if 'Fechamento' in df.columns:
            # Clean possible artifacts like extra quotes from CSV parsing
            df['Fechamento'] = df['Fechamento'].str.replace('"', '', regex=False)
            df['Fechamento_Dt'] = pd.to_datetime(df['Fechamento'].str.replace(',', ' ', regex=False), dayfirst=True, errors='coerce')
            df['Duration_Calc'] = df['Fechamento_Dt'] - df['Abertura_Dt']
        
        # Numeric Cleanups
        def clean_series(ser):
             return ser.astype(str).str.replace('R$', '', regex=False)\
                       .str.replace(' ', '', regex=False).str.replace('.', '', regex=False)\
                       .str.replace(',', '.', regex=False)\
                       .pipe(pd.to_numeric, errors='coerce').fillna(0.0)

        if 'Res. Intervalo Bruto' in df.columns:
            df['Res_Numeric'] = clean_series(df['Res. Intervalo Bruto'])
        else:
            df['Res_Numeric'] = 0.0

        if 'Preço Compra' in df.columns:
            df['Preço Compra Numeric'] = clean_series(df['Preço Compra'])
        if 'Preço Venda' in df.columns:
            df['Preço Venda Numeric'] = clean_series(df['Preço Venda'])

        # Balanced Qtd mapping (Avoid double-counting)
        if 'Qtd' in df.columns and 'Qtd Venda' in df.columns:
            # Vectorized maximum between Qtd and Qtd Venda
            q1 = clean_series(df['Qtd'])
            q2 = clean_series(df['Qtd Venda'])
            df['Qtd_Clean'] = np.maximum(q1, q2).astype(int)
        elif 'Qtd' in df.columns:
            df['Qtd_Clean'] = clean_series(df['Qtd']).astype(int)
        else:
            qtd_cols = [c for c in df.columns if 'qtd' in c.lower()]
            df['Qtd_Clean'] = clean_series(df[qtd_cols[0]]).astype(int) if qtd_cols else 0
            
        df = df.dropna(subset=['Abertura_Dt']).sort_values('Abertura_Dt')
        df['Cumulative'] = df['Res_Numeric'].cumsum()
        
        return df, name_map
    except Exception:
        return pd.DataFrame(), {}

@st.cache_data(ttl=1)
def _load_pattern_sheet():
    try:
        content = _get_raw_content(PATTERN_URL)
        if not content: return pd.DataFrame()
        
        # Robust delimiter detection for pattern sheet
        lines = content.splitlines()
        first_line = lines[0] if lines else ""
        sep = ';' if first_line.count(';') > first_line.count(',') else ','
        
        df_p = pd.read_csv(io.StringIO(content), sep=sep, on_bad_lines='skip')
        col_map = {}
        for c in df_p.columns:
            cl = c.lower()
            if 'setup' in cl and 'operado' in cl: col_map[c] = 'Pattern'
            elif 'setup' in cl and 'real' in cl: col_map[c] = 'RealPattern'
            elif 'tipo' in cl and 'ordem' in cl: col_map[c] = 'Tipo de Ordem'
            elif 'ativo' in cl: col_map[c] = 'Ativo'
            elif 'abertura' in cl: col_map[c] = 'Abertura'
            elif 'gerencia' in cl: col_map[c] = 'Management'
            elif 'mo' in cl or 'mao' in cl or 'mão' in cl: col_map[c] = 'HandError'
            elif 'tipo' in cl and 'ordem' in cl: col_map[c] = 'Tipo de Ordem'
        df_p = df_p.rename(columns=col_map)
        if 'Ativo' in df_p.columns and 'Abertura' in df_p.columns:
            df_p['Abertura_Dt'] = pd.to_datetime(df_p['Abertura'].astype(str).str.replace(',', ' ', regex=False), dayfirst=True, errors='coerce')
            if 'Pattern' not in df_p.columns: df_p['Pattern'] = "Não Classificado"
            if 'Tipo de Ordem' not in df_p.columns: df_p['Tipo de Ordem'] = "Não Classificado"
            if 'RealPattern' not in df_p.columns: df_p['RealPattern'] = df_p['Pattern']
            if 'Management' not in df_p.columns: df_p['Management'] = "Ok"
            if 'HandError' not in df_p.columns: df_p['HandError'] = "Sim"
            return df_p.dropna(subset=['Abertura_Dt', 'Ativo'])
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def normalize_pattern(val):
    if pd.isna(val) or str(val).strip().lower() in ['nan', '', 'não classificado']:
        return "Não Classificado"
    
    s = str(val).strip()
    s_low = s.lower()
    
    # Consolidation Logic: ONLY for the 3 groups explicitly requested by the user
    if "rompimento" in s_low: return "Rompimento"
    if "canal estreito" in s_low: return "Canal Estreito"
    if "canal amplo" in s_low: return "Canal Amplo"
    
    # For any other pattern, follow the spreadsheet EXACTLY
    return s

def load_pattern_data():
    return _load_pattern_sheet()

@st.cache_data(ttl=1)
def load_swing_trade_data():
    """Fetches and processes Swing Trade specific data."""
    SWING_URL = st.secrets.get("SWING_URL")
    if not SWING_URL:
        st.error("SWING_URL não configurado em st.secrets")
        return pd.DataFrame()
    try:
        content = _get_raw_content(SWING_URL)
        if not content: return pd.DataFrame()
        
        df = pd.read_csv(io.StringIO(content))
        
        # Standardize columns based on user description
        # 0: ID, 1: Data, 2: Ativo, 4: Periodo (1W/1M), 6: Entrou (Sim/Não), 7: Resultado, 8: Analista Geovanny, 9: Analista Rafaella
        new_cols = ['ID', 'Data', 'Ativo', 'Extra1', 'Periodo', 'Extra2', 'Entrou', 'Resultado', 'Analista Geovanny', 'Analista Rafaella']
        if len(df.columns) >= len(new_cols):
            df.columns = new_cols[:len(df.columns)]
        
        # Clean data
        df = df.dropna(subset=['Ativo'])
        df['Ativo'] = df['Ativo'].str.strip().str.upper()
        
        # --- NEW DEDUPLICATION & FILTERING LOGIC ---
        # 1. Ensure Data is datetime
        df['Data_Dt'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
        
        # 2. Filter for CLOSED operations
        # User said: "considerar sempre as operações encerradas (com data de entrada e saída definidas)"
        # Based on CSV inspection, open/tracking trades have '-', empty, or 'Acompanhando' in Resultado.
        invalid_results = ['-', '', 'ACOMPANHANDO', 'NAN']
        mask_closed = df['Resultado'].fillna('').str.strip().str.upper().apply(lambda x: x not in invalid_results)
        df_closed = df[mask_closed].copy()
        
        # Deduplication based on ID (keep the most recent entry for that ID)
        df_final = df_closed.drop_duplicates(subset=['ID'], keep='last')
        
        return df_final
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=3600)  # Cache market data for 1 hour
def fetch_real_ohlc(symbol, period_type='1W'):
    """
    Fetches the last 15 candles for a given B3 symbol.
    period_type: '1W' (Weekly) or '1M' (Monthly)
    """
    try:
        # Standardize ticker for Yahoo Finance (.SA suffix for B3)
        ticker = str(symbol).strip().upper()
        if not ticker.endswith('.SA') and not ticker.isdigit(): # Avoid adding .SA to indices or specific codes if needed
            ticker = f"{ticker}.SA"
            
        interval = "1wk" if '1W' in period_type.upper() else "1mo"
        # Download data (5y to ensure EMA 20 settlement/accuracy)
        data = yf.download(ticker, period="5y", interval=interval, progress=False)
        
        if data.empty:
            return pd.DataFrame()
            
        # Bulletproof flattening: handle MultiIndex and ensure string column names
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [str(c[0]) if isinstance(c, tuple) else str(c) for c in data.columns]
        else:
            data.columns = [str(c) for c in data.columns]
            
        # Standardize names to proper capitalization
        mapper = {c: c.strip().capitalize() for c in data.columns}
        data = data.rename(columns=mapper)
        
        # Ensure 'Close' exists (standard yfinance 0.2+)
        if 'Close' not in data.columns:
            if 'Adj close' in data.columns:
                data = data.rename(columns={'Adj close': 'Close'})
        
        data = data.sort_index()

        # Clean OHLC data BEFORE EMA calcs to avoid zero-bias
        for col in ['Open', 'High', 'Low', 'Close']:
            if col in data.columns:
                data[col] = data[col].replace(0, np.nan).ffill().bfill()

        # Calculate EMA 20 with adjust=True to match standard charting platforms
        data['EMA20'] = data['Close'].ewm(span=20, adjust=True).mean()

        # Take last 40 valid rows (we visualize 20, but keep history for EMA stability)
        return data.tail(40).reset_index()
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()
