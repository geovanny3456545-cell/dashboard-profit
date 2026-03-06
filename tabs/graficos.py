import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import datetime

def render(df, df_raw):
    """
    Renders optimized charts with shading, time slot efficiency, and setup comparisons.
    """
    if df.empty:
        st.info("Sem dados para exibir no momento.")
        return

    # Menu Options
    chart_opts = [
        "Gráfico de Resultados", 
        "Gráfico de Operações", 
        "Gráfico de Eficiência", 
        "Gráfico de Ordens", 
        "Gráfico por Periodo"
    ]
    
    chart_view = st.radio("Selecione o Gráfico:", chart_opts, horizontal=True, label_visibility="collapsed")
    st.markdown("---")
    
    # 1. Gráfico de Resultados (Equity) with Shading
    if chart_view == "Gráfico de Resultados":
        df_chart = df.copy().sort_values('Abertura_Dt').reset_index(drop=True)
        # RECALCULATE for current filtered period
        df_chart['Cumulative'] = df_chart['Res_Numeric'].cumsum()
        
        total_pnl = df_chart['Res_Numeric'].sum()
        num_trades = len(df_chart)
        win_rate = (len(df_chart[df_chart['Res_Numeric'] >= 0]) / num_trades * 100) if num_trades > 0 else 0
        
        c_pnl = "#00fa9a" if total_pnl > 0 else "#ff4d4d" if total_pnl < 0 else "#bbbbbb"
        
        st.markdown(f"""
        <div style="display: flex; background:#262626; padding:10px; border-radius:4px; gap:20px; font-size:14px; color:#ccc;">
            <div>Res. Liq: <span style="color:{c_pnl}; font-weight:bold;">R$ {total_pnl:,.2f}</span></div>
            <div>Ops: <b>{num_trades}</b></div>
            <div>Win Rate: <b style="color:#00fa9a;">{win_rate:.1f}%</b></div>
        </div>
        """, unsafe_allow_html=True)
        
        x_seq = np.arange(len(df_chart))
        y_vals = df_chart['Cumulative'].values
        
        # Line color logic
        line_color = '#00fa9a' if total_pnl > 0 else '#bbbbbb' if total_pnl == 0 else '#ff4d4d'
        # Fill color logic (RGBA)
        fill_rgba = "0, 250, 154, 0.15" if total_pnl > 0 else "255, 77, 77, 0.15" if total_pnl < 0 else "187, 187, 187, 0.1"
        
        fig = go.Figure()
        
        # Step Line for Equity (Standard Trading Style)
        fig.add_trace(go.Scatter(
            x=x_seq, y=y_vals,
            mode='lines+markers',
            line=dict(color=line_color, width=2, shape='hv'), # 'hv' for step-like movement
            marker=dict(
                size=5, 
                color=[("#00fa9a" if y > 0 else "#ff4d4d" if y < 0 else "#bbbbbb") for y in y_vals],
                line=dict(width=1, color="#121212")
            ),
            fill='tozeroy',
            fillcolor=f'rgba({fill_rgba})',
            name="Patrimônio",
            hovertemplate="<b>Operação %{x}</b><br>Saldo: R$ %{y:,.2f}<extra></extra>"
        ))
        
        fig.update_layout(
            title=dict(
                text="Performance Acumulada (Estilo ProfitPro)", 
                font=dict(size=18, color='#FFFFFF', family="Segoe UI, sans-serif")
            ),
            plot_bgcolor='#121212', 
            paper_bgcolor='#121212', 
            font=dict(color='#888', family="Segoe UI, sans-serif"),
            xaxis=dict(
                gridcolor='#252525', 
                zerolinecolor='#444', 
                title="Ordens Executadas",
                tickfont=dict(size=10)
            ),
            yaxis=dict(
                gridcolor='#252525', 
                zerolinecolor='#444', 
                title="Resultado Bruto (R$)",
                tickfont=dict(size=10)
            ),
            margin=dict(l=40, r=40, t=50, b=40),
            showlegend=False,
            hovermode="x unified"
        )
        fig.add_hline(y=0, line_dash="dash", line_color="#555", line_width=1)
        st.plotly_chart(fig, use_container_width=True, key="chart_equity_profit")

    # 2. Gráfico de Operações (Scatter Individual)
    elif chart_view == "Gráfico de Operações":
        st.markdown("### Resultado Individual por Operação")
        df_ops = df.copy().sort_values('Abertura_Dt').reset_index(drop=True)
        df_ops['Index'] = df_ops.index
        
        df_ops['Color'] = df_ops['Res_Numeric'].apply(lambda x: '#00fa9a' if x > 0 else '#ff4d4d' if x < 0 else '#bbbbbb')
        df_ops['Data_Formatada'] = df_ops['Abertura_Dt'].dt.strftime('%d/%m/%Y %H:%M')
        fig_ops = px.bar(df_ops, x='Index', y='Res_Numeric', color='Color',
                        color_discrete_map={'#00fa9a': '#00fa9a', '#ff4d4d': '#ff4d4d', '#bbbbbb': '#bbbbbb'},
                        hover_data={'Index': True, 'Res_Numeric': ':,.2f', 'Data_Formatada': True, 'Color': False})
        fig_ops.update_layout(plot_bgcolor='#1e1e1e', paper_bgcolor='#1e1e1e', font=dict(color='#ddd'), showlegend=False)
        st.plotly_chart(fig_ops, use_container_width=True, key="chart_ops")

    # 3. Gráfico de Eficiência (Setup Comparison)
    elif chart_view == "Gráfico de Eficiência":
        st.markdown("### Comparação: Setup Operado vs Setup Real")
        
        if 'Pattern_View' in df.columns and 'RealPattern_View' in df.columns:
            def get_eff(data, col):
                stats = []
                for pat, g in data.groupby(col):
                    if pat == "Não Classificado": continue
                    tot = len(g)
                    wr = (len(g[g['Res_Numeric'] > 0]) / tot * 100) if tot > 0 else 0
                    stats.append({"Setup": pat, "WinRate": wr, "Trades": tot})
                
                if not stats: return pd.DataFrame(columns=["Setup", "WinRate", "Trades"])
                return pd.DataFrame(stats).sort_values('WinRate', ascending=False)

            df_op = get_eff(df, 'Pattern_View')
            df_re = get_eff(df, 'RealPattern_View')
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### Setup Operado")
                if not df_op.empty:
                    fig_op = px.bar(df_op, x='Setup', y='WinRate', color_discrete_sequence=['#00fa9a'], range_y=[0, 100])
                    fig_op.update_layout(height=400, plot_bgcolor='#1e1e1e', paper_bgcolor='#1e1e1e', font=dict(color='#ddd'))
                    st.plotly_chart(fig_op, use_container_width=True, key="chart_eff_op")
                else: st.info("Sem dados de Setup Operado")

            with c2:
                st.markdown("#### Setup Real")
                if not df_re.empty:
                    fig_re = px.bar(df_re, x='Setup', y='WinRate', color_discrete_sequence=['#00fa9a'], range_y=[0, 100])
                    fig_re.update_layout(height=400, plot_bgcolor='#1e1e1e', paper_bgcolor='#1e1e1e', font=dict(color='#ddd'))
                    st.plotly_chart(fig_re, use_container_width=True, key="chart_eff_re")
                else: st.info("Sem dados de Setup Real")

            # --- Technical Error Analysis (Al Brooks Checklist) ---
            st.markdown("---")
            st.markdown("#### ⚙️ Análise de Erros Técnicos (Por Ciclo de Mercado)")
            
            # Prepare error flags
            df_err = df.copy()
            df_err['Cycle_Error'] = df_err['Pattern_View'] != df_err['RealPattern_View']
            df_err['Mgmt_Error'] = df_err['Management'].astype(str).str.lower().apply(lambda x: x not in ['ok', 'sim', 'sucesso', 'nan', ''])
            df_err['Hand_Error'] = df_err['HandError'].astype(str).str.lower().apply(lambda x: x not in ['sim', 'ok', 'sucesso', 'nan', ''])
            
            error_stats = []
            for cycle, g in df_err.groupby('RealPattern_View'):
                if cycle == "Não Classificado": continue
                tot = len(g)
                c_err = g['Cycle_Error'].sum()
                m_err = g['Mgmt_Error'].sum()
                h_err = g['Hand_Error'].sum()
                
                if c_err > 0 or m_err > 0 or h_err > 0:
                    # Calculate breakdown of WRONG classifications for the "zoom"
                    mismatches = g[g['Cycle_Error'] == True]['Pattern_View']
                    breakdown = mismatches.value_counts(normalize=True) * 100
                    
                    error_stats.append({
                        "Ciclo": cycle,
                        "Erro Ciclo": c_err,
                        "Erro Gerenc.": m_err,
                        "Mão Incorreta": h_err,
                        "Total Ops": tot,
                        "Breakdown": breakdown.to_dict()
                    })

            # Custom sort by cycle order
            cycle_order = {"Rompimento": 1, "Canal Estreito": 2, "Canal Amplo": 3, "Lateralidade": 4}
            def sort_key(stat):
                return cycle_order.get(stat['Ciclo'], 99)
            
            error_stats = sorted(error_stats, key=sort_key)

            if error_stats:
                cols = st.columns(len(error_stats))
                for i, stat in enumerate(error_stats):
                    # Build classification zoom HTML if errors exist
                    if stat['Erro Ciclo'] > 0:
                        breakdown_rows = "".join([
                            f'<div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:2px; border-bottom:1px solid #333;">'
                            f'<span style="color:#ccc;">{p}</span><span style="color:#00fa9a;">{pct:.0f}%</span></div>'
                            for p, pct in stat['Breakdown'].items()
                        ])
                        class_html = f"""<details style="cursor:pointer; margin-bottom:5px;">
<summary style="display:flex; justify-content:space-between; font-size:13px; list-style:none; outline:none;">
<span style="color:#aaa;">Erro Classificação:</span>
<span style="color:#ff4d4d; font-weight:bold;">{stat['Erro Ciclo']} ▼</span>
</summary>
<div style="background:#1e1e1e; padding:8px; border-radius:3px; margin-top:5px;">
<div style='font-size:11px; color:#999; margin-bottom:5px;'>Classificou erroneamente como:</div>
{breakdown_rows}
</div>
</details>"""
                    else:
                        class_html = f"""<div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:5px;">
<span style="color:#aaa;">Erro Classificação:</span>
<span style="color:#888; font-weight:bold;">0</span>
</div>"""

                    with cols[i % len(cols)]:
                        card_html = f"""<div style="background:#2b2b2b; padding:15px; border-radius:4px; border-top:3px solid #ff4d4d; margin-bottom:5px;">
<div style="color:#fff; font-weight:bold; font-size:1.1em; margin-bottom:10px;">{stat['Ciclo']}</div>
{class_html}
<div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:5px;">
<span style="color:#aaa;">Erro Gerenc.:</span>
<span style="color:{'#ff4d4d' if stat['Erro Gerenc.'] > 0 else '#888'}; font-weight:bold;">{stat['Erro Gerenc.']}</span>
</div>
<div style="display:flex; justify-content:space-between; font-size:13px;">
<span style="color:#aaa;">Mão Incorreta:</span>
<span style="color:{'#ff4d4d' if stat['Mão Incorreta'] > 0 else '#888'}; font-weight:bold;">{stat['Mão Incorreta']}</span>
</div>
</div>
<div style="font-size:11px; color:#666; text-align:right; margin-top:5px; padding-right:5px;">
em {stat['Total Ops']} operações
</div>"""
                        st.markdown(card_html, unsafe_allow_html=True)
            else:
                st.info("Nenhum erro de classificação, gerenciamento ou mão detectado para os filtros atuais.")

    # 4. Gráfico de Ordens (Stop vs Limite Boxes)
    elif chart_view == "Gráfico de Ordens":
        st.markdown("### Estatísticas por Tipo de Ordem")
        
        if 'Tipo de Ordem' in df.columns:
            df_ord = df[df['Tipo de Ordem'] != 'Não Classificado']
            
            if not df_ord.empty:
                ord_stats = []
                for t in ["Ordem Stop", "Ordem Limite"]:
                    g = df_ord[df_ord['Tipo de Ordem'] == t]
                    tot = len(g)
                    if tot == 0: continue
                    res = g['Res_Numeric'].sum()
                    wr = (len(g[g['Res_Numeric'] > 0]) / tot * 100)
                    ord_stats.append({"Tipo": t, "Resultado": res, "Trades": tot, "WinRate": wr})
                
                if ord_stats:
                    cols = st.columns(len(ord_stats))
                    for i, stat in enumerate(ord_stats):
                        c_res = "#00fa9a" if stat['Resultado'] > 0 else "#ff4d4d" if stat['Resultado'] < 0 else "#bbbbbb"
                        with cols[i]:
                            st.markdown(f"""
                            <div style="background:#2b2b2b; padding:15px; border-radius:4px; border:1px solid #444; text-align:center;">
                                <div style="color:#aaa; font-size:0.9em; margin-bottom:5px;">{stat['Tipo']}</div>
                                <div style="font-size:1.5em; font-weight:bold; color:{c_res};">R$ {stat['Resultado']:,.2f}</div>
                                <div style="color:#ddd; font-size:0.9em; margin-top:5px;">{stat['Trades']} trades | {stat['WinRate']:.1f}% WR</div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("Nenhuma Ordem Stop ou Limite encontrada nos dados filtrados.")
            else:
                st.info("Dados de ordens não classificados.")
        else:
            st.error("Coluna 'Tipo de Ordem' não encontrada.")

    # 5. Gráfico por Periodo (Efficiency)
    elif chart_view == "Gráfico por Periodo":
        st.markdown("### Eficiência por Horário")
        
        df_per = df.copy()
        if 'Abertura_Dt' in df_per.columns:
            df_per['Hour'] = df_per['Abertura_Dt'].dt.hour
            
            def get_slot(h):
                if 9 <= h < 10: return "1ª Hora (9h)"
                if 10 <= h < 11: return "2ª Hora (10h)"
                if 11 <= h < 12: return "3ª Hora (11h)"
                if h >= 12: return "Tarde (12h+)"
                return "Outros"

            df_per['Slot'] = df_per['Hour'].apply(get_slot)
            slots = ["1ª Hora (9h)", "2ª Hora (10h)", "3ª Hora (11h)", "Tarde (12h+)"]
            
            plot_data = []
            for s in slots:
                g = df_per[df_per['Slot'] == s]
                tot = len(g)
                if tot == 0: continue
                p_gain = len(g[g['Res_Numeric'] > 0]) / tot * 100
                p_loss = len(g[g['Res_Numeric'] < 0]) / tot * 100
                p_be = len(g[g['Res_Numeric'] == 0]) / tot * 100
                plot_data.extend([
                    {"Slot": s, "Tipo": "Gain", "Percent": p_gain},
                    {"Slot": s, "Tipo": "Loss", "Percent": p_loss},
                    {"Slot": s, "Tipo": "BE", "Percent": p_be}
                ])
            
            if plot_data:
                fig_slot = px.bar(pd.DataFrame(plot_data), x='Slot', y='Percent', color='Tipo',
                                 color_discrete_map={'Gain': '#00fa9a', 'Loss': '#ff4d4d', 'BE': '#bbbbbb'},
                                 title="Eficiência por Slot (%)", barmode='stack')
                fig_slot.update_layout(plot_bgcolor='#1e1e1e', paper_bgcolor='#1e1e1e', font=dict(color='#ddd'), height=450)
                st.plotly_chart(fig_slot, use_container_width=True, key="chart_slots")

    # 6. Global Pattern Analysis (Metrics) - Always show at bottom
    if 'Pattern_View' in df_raw.columns:
        st.markdown("---")
        st.markdown("### Análise Global por Padrão")
        
        def get_pstats(data, col):
            stats = []
            for pat, g in data.groupby(col):
                if pat == "Não Classificado": continue
                res = g['Res_Numeric'].sum()
                cnt = len(g)
                # Calculate Win Rate
                wins = len(g[g['Res_Numeric'] > 0])
                wr = (wins / cnt * 100) if cnt > 0 else 0
                stats.append({"Pattern": pat, "Result": res, "Trades": cnt, "WinRate": wr})
            return pd.DataFrame(stats).sort_values('Result', ascending=False)
        
        df_p_global = get_pstats(df_raw, 'RealPattern_View')
        
        if not df_p_global.empty:
            m1, m2 = st.columns(2)
            best = df_p_global.iloc[0]
            worst = df_p_global.iloc[-1]
            
            best_color = "#00fa9a" if best['Result'] > 0 else "#ff4d4d" if best['Result'] < 0 else "#bbbbbb"
            worst_color = "#00fa9a" if worst['Result'] > 0 else "#ff4d4d" if worst['Result'] < 0 else "#bbbbbb"
            
            with m1:
                st.markdown(f"""
                <div style="margin-bottom: 10px;">
                    <div style="color: #888; font-size: 0.85em;">Melhor Padrão</div>
                    <div style="color: #fff; font-size: 1.2em; font-weight: bold; margin-bottom: 2px;">{best['Pattern']}</div>
                    <div style="color: {best_color}; font-size: 1.5em; font-weight: bold;">R$ {best['Result']:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with m2:
                st.markdown(f"""
                <div style="margin-bottom: 10px;">
                    <div style="color: #888; font-size: 0.85em;">Pior Padrão</div>
                    <div style="color: #fff; font-size: 1.2em; font-weight: bold; margin-bottom: 2px;">{worst['Pattern']}</div>
                    <div style="color: {worst_color}; font-size: 1.5em; font-weight: bold;">R$ {worst['Result']:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            df_p_global['Color'] = df_p_global['Result'].apply(lambda x: '#00fa9a' if x > 0 else '#ff4d4d' if x < 0 else '#bbbbbb')
            fig_p = px.bar(
                df_p_global, x='Pattern', y='Result', color='Color', 
                color_discrete_map={'#00fa9a': '#00fa9a', '#ff4d4d': '#ff4d4d', '#bbbbbb': '#bbbbbb'}, 
                title="Resultado Global por Padrão",
                hover_data={'Pattern': True, 'Result': ':,.2f', 'Trades': True, 'WinRate': ':.1f%', 'Color': False}
            )
            fig_p.update_layout(plot_bgcolor='#1e1e1e', paper_bgcolor='#1e1e1e', font=dict(color='#ddd'), coloraxis_showscale=False, showlegend=False)
            st.plotly_chart(fig_p, use_container_width=True, key="chart_global_pattern")
