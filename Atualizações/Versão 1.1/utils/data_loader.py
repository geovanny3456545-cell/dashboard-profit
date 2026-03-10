import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import csv
import datetime

# --- Constants & Config ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=872600748&single=true&output=csv"
PATTERN_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=2017205813&single=true&output=csv"

def load_data():
    """Main entry for unified data loading with multi-layer caching."""
    try:
        df, name_map = _load_performance_report()
        if df.empty:
            return pd.DataFrame(), {}
            
        df_p = _load_pattern_sheet()
        
        if not df_p.empty:
            # Vectorized Merge Keys
            df['Ativo_Key'] = df['Ativo'].astype(str).str.strip().str.upper()
            df_p['Ativo_Key'] = df_p['Ativo'].astype(str).str.strip().str.upper()
            
            # Robust Timestamp Rounding (Floor to minute)
            df['Merge_Dt'] = df['Abertura_Dt'].dt.floor('min')
            df_p['Merge_Dt'] = df_p['Abertura_Dt'].dt.floor('min')

            # Clean possible stale columns from performance report before merge
            for col in ['Pattern', 'RealPattern', 'Tipo de Ordem', 'Observation', 'Management', 'HandError', 'Pattern_View', 'RealPattern_View']:
                if col in df.columns:
                    df = df.drop(columns=[col])

            # Optimized Merge - Keep LAST entry from spreadsheet if duplicates exist
            cols_to_use = ['Ativo_Key', 'Merge_Dt', 'Pattern', 'RealPattern', 'Tipo de Ordem', 'Management', 'HandError']
            df_p_clean = df_p.drop_duplicates(subset=['Ativo_Key', 'Merge_Dt'], keep='last')
            
            df = df.merge(df_p_clean[cols_to_use], on=['Ativo_Key', 'Merge_Dt'], how='left')
            
            # Defaults
            df['Pattern'] = df['Pattern'].fillna("Não Classificado")
            df['RealPattern'] = df['RealPattern'].fillna(df['Pattern'])
            df['Tipo de Ordem'] = df['Tipo de Ordem'].fillna("Não Classificado")
            df['Management'] = df['Management'].fillna("Ok")
            df['HandError'] = df['HandError'].fillna("Sim") # Mão correta: Sim (default)
            
            df['Pattern_View'] = df['Pattern'].map(normalize_pattern)
            df['RealPattern_View'] = df['RealPattern'].map(normalize_pattern)
            
            df = df.drop(columns=['Ativo_Key', 'Merge_Dt'])

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
                sep = ';' if line.count(';') > line.count(',') else ','
                break
        
        if header_idx == -1: return pd.DataFrame(), {}
        
        f = io.StringIO(content)
        for _ in range(header_idx): f.readline()
        
        header_line = f.readline().strip()
        reader_h = csv.reader(io.StringIO(header_line), delimiter=sep)
        headers = next(reader_h)
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
            if 'ativo' in cl and 'ag' not in cl: name_map[c] = 'Ativo'
            elif 'abertura' in cl: name_map[c] = 'Abertura'
            elif 'fechamento' in cl and 'hora' not in cl: name_map[c] = 'Fechamento'
            elif 'res' in cl and 'bruto' in cl: name_map[c] = 'Res. Intervalo Bruto'
            elif 'lado' in cl: name_map[c] = 'Lado'
            elif 'qtd' in cl and not found_qtd:
                # Map only the FIRST Qtd-related column found to 'Qtd'
                # ProfitPro typically has Qtd Compra followed by Qtd Venda
                # We will handle the actual quantity cleanup below
                name_map[c] = 'Qtd'
                found_qtd = True

        df = df.rename(columns=name_map)
        
        # Vectorized Parsing
        if 'Abertura' in df.columns:
            df['Abertura_Dt'] = pd.to_datetime(df['Abertura'].str.replace(',', ' ', regex=False), dayfirst=True, errors='coerce')
            df['Date'] = df['Abertura_Dt'].dt.date
        
        if 'Fechamento' in df.columns:
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
            elif 'mão' in cl: col_map[c] = 'HandError'
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
