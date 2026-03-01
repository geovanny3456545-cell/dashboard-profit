import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import plotly.graph_objects as go
from utils.data_loader import fetch_real_ohlc
import datetime
import yfinance as yf
import numpy as np

@st.cache_data(ttl=3600)
def get_batch_market_data(proxies_to_fetch):
    """Fetches markert data for multiple symbols in one go with caching."""
    results = {}
    for sym, d_range in proxies_to_fetch.items():
        p_start = d_range['start'].replace(hour=0, minute=0, second=0) - datetime.timedelta(days=1)
        p_end = d_range['end'].replace(hour=23, minute=59, second=59) + datetime.timedelta(days=1)
        
        try:
            df = yf.download(sym, start=p_start, end=p_end, interval='5m', progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = [str(c[0]) for c in df.columns]
                results[sym] = df
            else:
                results[sym] = pd.DataFrame()
        except:
            results[sym] = pd.DataFrame()
    return results

def render(df, df_raw):
    # Calculate performance metrics
    total_pnl = df['Res_Numeric'].sum()
    gross_profit = df[df['Res_Numeric'] > 0]['Res_Numeric'].sum()
    gross_loss = df[df['Res_Numeric'] < 0]['Res_Numeric'].sum()
    num_trades = len(df)
    win_rate = (len(df[df['Res_Numeric'] > 0]) / num_trades * 100) if num_trades > 0 else 0
    
    # --- PROFIT PRO HEADER STRIP ---
    s_res_liq = f"R$ {total_pnl:,.2f}"
    s_res_tot = f"R$ {total_pnl:,.2f}"
    s_lucro = f"R$ {gross_profit:,.2f}"
    s_prej = f"R$ {gross_loss:,.2f}"
    s_ops = f"{num_trades}"
    s_win = f"{win_rate:.2f}%"
    s_custos = "R$ 0,00" # Placeholder
    
    # Colors
    c_res = "#00fa9a" if total_pnl > 0 else "#ff4d4d" if total_pnl < 0 else "#bbbbbb"
    
    html_strip = f"""
    <style>
        .strip-container {{
            display: flex;
            flex-direction: row;
            background-color: #262626;
            padding: 8px 15px;
            border-radius: 4px;
            margin-bottom: 10px;
            align-items: center;
            font-family: 'Segoe UI', sans-serif;
            font-size: 14px;
            color: #ccc;
            gap: 15px;
            overflow-x: auto;
        }}
        .strip-item {{
            display: flex;
            flex-direction: row;
            gap: 5px;
            white-space: nowrap;
        }}
        .strip-val {{ font-weight: bold; }}
        .color-pos {{ color: #00fa9a; }}
        .color-neg {{ color: #ff6b6b; }}
    </style>
    <div class="strip-container">
        <div class="strip-item">Resultado Liq Tot. <span class="strip-val" style="color:{c_res}">{s_res_liq}</span></div>
        <div style="width:1px; height:15px; background:#444;"></div>
        <div class="strip-item">Resultado Total <span class="strip-val" style="color:{c_res}">{s_res_tot}</span></div>
        <div style="width:1px; height:15px; background:#444;"></div>
        <div class="strip-item">Lucro Bruto <span class="strip-val color-pos">{s_lucro}</span></div>
        <div style="width:1px; height:15px; background:#444;"></div>
        <div class="strip-item">Prejuízo Bruto <span class="strip-val color-neg">{s_prej}</span></div>
        <div style="width:1px; height:15px; background:#444;"></div>
        <div class="strip-item">Operações <span class="strip-val">{s_ops}</span></div>
        <div style="width:1px; height:15px; background:#444;"></div>
        <div class="strip-item">Vencedoras <span class="strip-val">{s_win}</span></div>
        <div style="width:1px; height:15px; background:#444;"></div>
        <div class="strip-item">Custos <span class="strip-val">{s_custos}</span></div>
    </div>
    """
    st.markdown(html_strip, unsafe_allow_html=True)

    # --- RECENT OPERATIONS CARDS (Horizontal Layout) ---
    if not df.empty:
        st.markdown("### 🎯 Foco Principal: Operações Recentes (5m)")
        
        # Sort by Date desc
        sorted_df = df.sort_values('Abertura_Dt', ascending=False)
        
        # --- BATCH DATA FETCHING PER SYMBOL ---
        proxies_to_fetch = {}
        for _, row in sorted_df.iterrows():
            sym = "^BVSP" if "WIN" in str(row['Ativo']).upper() else "USDBRL=X"
            if sym not in proxies_to_fetch:
                proxies_to_fetch[sym] = {'start': row['Abertura_Dt'], 'end': row.get('Fechamento_Dt', row['Abertura_Dt'])}
            else:
                proxies_to_fetch[sym]['start'] = min(proxies_to_fetch[sym]['start'], row['Abertura_Dt'])
                proxies_to_fetch[sym]['end'] = max(proxies_to_fetch[sym]['end'], row.get('Fechamento_Dt', row['Abertura_Dt']))

        # Use the cached batch fetcher
        proxy_data = get_batch_market_data(proxies_to_fetch)

        # Render cards
        for idx, row in sorted_df.iterrows():
            # Auto-expand only first 5
            is_expanded = (idx < 5)
            
            with st.expander(f"{row['Ativo']} | {row['Abertura']} | Resultado: {row['Res. Operação']}", expanded=is_expanded):
                col1, col2, col3 = st.columns([1.5, 3, 2.5])
                
                with col1:
                    st.metric("Ativo", row['Ativo'])
                    st.write(f"**Lado:** {row['Lado']}")
                    st.write(f"**Qtd:** {row['Qtd']}")
                    st.caption(f"📅 {row['Abertura']}")
                
                with col2:
                    symbol_proxy = "^BVSP" if "WIN" in str(row['Ativo']).upper() else "USDBRL=X"
                    st.write(f"**Gráfico 5m ({symbol_proxy})**")
                    
                    side = str(row.get('Lado', 'C')).strip().upper()
                    def get_price(p_col_numeric, p_col_raw):
                        val = row.get(p_col_numeric, row.get(p_col_raw, 0))
                        if isinstance(val, str):
                             val = val.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
                             try: val = float(val)
                             except: val = 0
                        return val

                    p_compra = get_price('Preço Compra Numeric', 'Preço Compra')
                    p_venda = get_price('Preço Venda Numeric', 'Preço Venda')
                    entry_px = p_compra if side == 'C' else p_venda
                    exit_px = p_venda if side == 'C' else p_compra
                    exit_dt = row.get('Fechamento_Dt', row['Abertura_Dt'])
                    
                    # Pass the pre-fetched data
                    df_symbol = proxy_data.get(symbol_proxy, pd.DataFrame())
                    fig = render_daytrade_sparkline(
                        df_symbol, 
                        row['Abertura_Dt'], 
                        exit_dt, 
                        entry_px, 
                        exit_px, 
                        side
                    )
                    st.plotly_chart(fig, config={'displayModeBar': False}, use_container_width=True, key=f"dt_card_chart_{idx}")
                
                with col3:
                    st.write("**📊 Detalhes da Execução:**")
                    st.write(f"- **Preço Médio:** {row['Médio']}")
                    st.write(f"- **Resultado Bruto:** {row['Res. Intervalo Bruto']}")
                    res_val = row['Res_Numeric']
                    res_color = "green" if res_val > 0 else "red" if res_val < 0 else "gray"
                    st.markdown(f"- **P/L Final:** :{res_color}[{row['Res. Operação']}]")
                    st.write(f"- **Tempo:** {row['Tempo Operação']}")

    st.markdown("---")

    # --- TOP SCROLL BAR COMPONENT ---
    components.html("""
        <style>
            #top-scroll-wrapper {
                width: 100%;
                overflow-x: auto;
                overflow-y: hidden;
                height: 16px;
                background: #1e1e1e;
                border-radius: 4px;
                margin-bottom: 5px;
            }
            #top-scroll-content { height: 16px; }
            ::-webkit-scrollbar { height: 8px; }
            ::-webkit-scrollbar-thumb { background: #555; border-radius: 4px; }
        </style>
        <div id="top-scroll-wrapper"><div id="top-scroll-content"></div></div>
        <script>
            const sync = () => {
                const wrapper = document.getElementById('top-scroll-wrapper');
                const content = document.getElementById('top-scroll-content');
                const parent = window.parent.document;
                const dataframes = parent.querySelectorAll('[data-testid="stDataFrame"]');
                
                if (dataframes.length > 0 && wrapper && content) {
                    const df = dataframes[0];
                    const scrollable = df.querySelector('.glideDataEditor') || df.querySelector('div[overflow="auto"]') || df;
                    
                    content.style.width = scrollable.scrollWidth + 'px';
                    wrapper.onscroll = () => { scrollable.scrollLeft = wrapper.scrollLeft; };
                    scrollable.onscroll = () => { wrapper.scrollLeft = scrollable.scrollLeft; };
                }
            };
            setInterval(sync, 2000);
        </script>
    """, height=30)

    # --- DATAFRAME ---
    target_cols = [
        'Ativo', 'Abertura', 'Fechamento', 'Tempo Operação', 
        'Pattern_View', 'Tipo de Ordem', # Manual Classifications
        'Qtd', 'Lado', # Combined
        'Preço Compra', 'Preço Venda', 'Preço de Mercado', 
        'MEP', 'MEN', 
        'Ag. Compra', 'Ag. Venda', 'Médio', 
        'Res. Intervalo Bruto', 'Res. Intervalo (%)', 
        'Número Operação', 'Res. Operação', 'Res. Operação (%)', 
        'Drawdown', 'Ganho Max.', 'Perda Max.', 'TET', 'Total'
    ]
    
    if not df.empty:
        df_show = df.copy()
        
        # Create Qtd Display Column
        def fmt_qtd(row):
            q = int(row.get('Qtd_Clean', 0))
            l = str(row.get('Lado', '')).strip()
            prefix = "-" if l == 'V' else ""
            return f"{prefix}{q} {l}"
        
        df_show['Qtd'] = df_show.apply(fmt_qtd, axis=1)
        
        # Ensure we have the list
        cols_to_show = [c for c in target_cols if c in df_show.columns]
        
        # Sort by Date desc
        df_show = df_show.sort_values('Abertura_Dt', ascending=False)
        
        # Styling
        s = df_show[cols_to_show].style
        
        # 1. Colors
        color_cols = [
            'MEP', 'MEN', 'Res. Intervalo Bruto', 'Res. Operação', 
            'Drawdown', 'Ganho Max.', 'Perda Max.', 'TET', 'Total', 'Res. Intervalo (%)', 'Res. Operação (%)'
        ]
        valid_color_cols = [c for c in color_cols if c in cols_to_show]
        
        def color_val(v):
            if pd.isna(v) or v == '': return ''
            s_v = str(v).strip().replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
            try:
                val = float(s_v)
                if val == 0: return 'color: #888;' # Grey for zero
                return 'color: #00fa9a;' if val > 0 else 'color: #ff4d4d;'
            except:
                return ''
        
        s.map(color_val, subset=valid_color_cols)
        
        # 2. Qtd Styling
        def style_qtd(v):
            if pd.isna(v): return ''
            s_v = str(v)
            if 'V' in s_v: return 'color: #ff4d4d; font-weight: bold;' 
            if 'C' in s_v: return 'color: #00fa9a; font-weight: bold;'
            return ''
            
        if 'Qtd' in cols_to_show:
            s.map(style_qtd, subset=['Qtd'])

        st.dataframe(
            s,
            use_container_width=True,
            height=600
        )

def render_daytrade_sparkline(full_df, entry_dt, exit_dt, entry_px, exit_px, side):
    """Generates a 5m candlestick chart aligned with entry price, handling TZ gaps."""
    try:
        if full_df is None or full_df.empty:
            fig = go.Figure()
            fig.add_annotation(text="Sem dados de mercado (5m)", showarrow=False, font=dict(size=10, color="gray"))
            return fig

        # --- TIMEZONE & SLICING LOGIC ---
        # 1. Normalize market data to naive local (BRT is typically UTC-3)
        # yfinance index usually comes in UTC
        working_df = full_df.copy()
        if working_df.index.tz is not None:
            # Convert to Brazil/Sao_Paulo then strip TZ to match Excel/CSV dates
            working_df.index = working_df.index.tz_convert('America/Sao_Paulo').tz_localize(None)
        
        # 2. Slice with a wider window to ensure we catch the data
        # Increase window to 2 hours before/after to be safe
        start_range = entry_dt - datetime.timedelta(hours=2)
        end_range = exit_dt + datetime.timedelta(hours=2)
        
        df = working_df.loc[start_range:end_range].copy()

        # 3. Fallback: If still empty, try to find the 20 closest candles to entry_dt
        if df.empty:
            iloc_idx = working_df.index.get_indexer([entry_dt], method='nearest')[0]
            start_iloc = max(0, iloc_idx - 10)
            end_iloc = min(len(working_df), iloc_idx + 10)
            df = working_df.iloc[start_iloc:end_iloc].copy()

        if df.empty:
            fig = go.Figure()
            fig.add_annotation(text="Aguardando dados intraday...", showarrow=False, font=dict(size=10, color="gray"))
            return fig
            
        # --- ALIGNMENT LOGIC ---
        try:
            closest_idx = df.index.get_indexer([entry_dt], method='nearest')[0]
            market_at_entry = df['Close'].iloc[closest_idx]
            offset = entry_px - market_at_entry
        except:
            offset = 0

        # Apply offset to all OHLC data
        for col in ['Open', 'High', 'Low', 'Close']:
            df[col] = df[col] + offset
        
        df['EMA20'] = df['Close'].ewm(span=20, adjust=True).mean()
        
        color_up = '#00fa9a'
        color_down = '#ff4d4d'
        
        fig = go.Figure(data=[
            go.Candlestick(
                x=df.index,
                open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                increasing=dict(line=dict(color=color_up), fillcolor=color_up),
                decreasing=dict(line=dict(color=color_down), fillcolor=color_down),
                whiskerwidth=0.3,
                name="Preço"
            )
        ])
        
        # Add EMA Segments
        for i in range(1, len(df)):
            seg_color = color_up if df['Close'].iloc[i] > df['EMA20'].iloc[i] else color_down
            fig.add_trace(go.Scatter(
                x=df.index[i-1:i+1], y=df['EMA20'].iloc[i-1:i+1],
                mode='lines', line=dict(color=seg_color, width=1.5), showlegend=False
            ))
            
        # --- ENTRY/EXIT MARKERS ---
        entry_marker = "triangle-up" if side == 'C' else "triangle-down"
        entry_color = "#00fa9a" if side == 'C' else "#ff4d4d"
        exit_marker = "triangle-down" if side == 'C' else "triangle-up"
        exit_color = "#ffcc00"
        
        fig.add_trace(go.Scatter(
            x=[entry_dt], y=[entry_px],
            mode='markers',
            marker=dict(symbol=entry_marker, size=12, color=entry_color, line=dict(width=1, color="white")),
            name="Entrada",
            hovertemplate=f"Entrada: {entry_px:,.2f}<extra></extra>"
        ))
        
        fig.add_trace(go.Scatter(
            x=[exit_dt], y=[exit_px],
            mode='markers',
            marker=dict(symbol=exit_marker, size=12, color=exit_color, line=dict(width=1, color="white")),
            name="Saída",
            hovertemplate=f"Saída: {exit_px:,.2f}<extra></extra>"
        ))
        
        fig.add_trace(go.Scatter(
            x=[entry_dt, exit_dt], y=[entry_px, exit_px],
            mode='lines',
            line=dict(color="rgba(255,255,255,0.4)", width=1, dash="dot"),
            showlegend=False, hoverinfo='skip'
        ))
        
        # Dynamic Zoom
        y_min = min(df['Low'].min(), entry_px, exit_px) * 0.9997
        y_max = max(df['High'].max(), entry_px, exit_px) * 1.0003

        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(visible=False), 
            yaxis=dict(
                visible=True, showticklabels=True, tickfont=dict(size=8, color="gray"), side="right",
                range=[y_min, y_max]
            ),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            xaxis_rangeslider_visible=False, height=220
        )
        return fig
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Erro visual: {str(e)}", showarrow=False, font=dict(size=10, color="red"))
        return fig
