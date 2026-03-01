import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

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
