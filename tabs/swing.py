import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_loader import fetch_real_ohlc
from utils.sector_map import get_sector

def render_sparkline(symbol, period):
    """Generates a tiny candlestick chart using real B3 market data."""
    df = fetch_real_ohlc(symbol, period)
    
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Sem Dados", showarrow=False, font=dict(size=10, color="gray"))
        fig.update_layout(width=120, height=50, margin=dict(l=0, r=0, t=0, b=0),
                         xaxis=dict(visible=False), yaxis=dict(visible=False),
                         plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        return fig

    # OHLC Cleaning now handled upstream in data_loader.py

    # Slice data to last 20 bars for display as requested
    df_display = df.tail(20).copy()
    
    color_up = '#00fa9a'   # Standard Green
    color_down = '#ff4d4d' # Standard Red
    
    latest_close = df_display['Close'].iloc[-1]
    latest_ema = df_display['EMA20'].iloc[-1]
    
    # Base figure with Candlesticks
    fig = go.Figure(data=[
        go.Candlestick(
            x=df_display.index,
            open=df_display['Open'], high=df_display['High'], low=df_display['Low'], close=df_display['Close'],
            increasing=dict(line=dict(color=color_up), fillcolor=color_up),
            decreasing=dict(line=dict(color=color_down), fillcolor=color_down),
            whiskerwidth=0.3,
            hoverinfo='text',
            text=[f"Data: {d.strftime('%d/%m/%Y')}<br>A: {o:.2f}<br>M: {h:.2f}<br>m: {l:.2f}<br>F: {c:.2f}" 
                  for d, o, h, l, c in zip(df_display['Date'], df_display['Open'], df_display['High'], df_display['Low'], df_display['Close'])]
        )
    ])
    
    # Add Segmented EMA line
    # We iterate and create segments to change colors at each bar if needed
    for i in range(1, len(df_display)):
        # Color based on the point we are arriving at (index i)
        seg_color = color_up if df_display['Close'].iloc[i] > df_display['EMA20'].iloc[i] else color_down
        
        fig.add_trace(go.Scatter(
            x=df_display.index[i-1:i+1],
            y=df_display['EMA20'].iloc[i-1:i+1],
            mode='lines',
            line=dict(color=seg_color, width=1.5),
            hoverinfo='skip',
            showlegend=False
        ))
    
    # Determine latest EMA color for the annotation
    latest_ema_color = color_up if latest_close > latest_ema else color_down

    # Add EMA 20 Value Annotation
    # If EMA and Close are too close, shift EMA slightly to avoid overlap
    ema_yshift = 0
    price_range = df_display['High'].max() - df_display['Low'].min()
    if abs(latest_close - latest_ema) < price_range * 0.05:
        ema_yshift = 10 if latest_ema > latest_close else -10

    fig.add_annotation(
        x=df_display.index[-1],
        y=latest_ema,
        text=f"{latest_ema:.2f}",
        showarrow=False,
        xanchor="left",
        xshift=10, # Move further right
        yshift=ema_yshift,
        font=dict(size=9, color=latest_ema_color, family="Arial"),
        bgcolor="rgba(0,0,0,0.6)"
    )

    # Add Latest Close Price Annotation - Perfectly aligned with the close level
    fig.add_annotation(
        x=df_display.index[-1],
        y=latest_close,
        text=f"{latest_close:.2f}",
        showarrow=False,
        xanchor="left",
        xshift=10, # Move further right
        yshift=0,  # Zero shift for perfect horizontal alignment
        font=dict(size=10, color="#ffffff", family="Arial"),
        bgcolor="rgba(0,0,0,0.8)"
    )
    
    fig.update_layout(
        margin=dict(l=0, r=55, t=0, b=0), # Larger right margin for labels
        xaxis=dict(visible=False, showgrid=False), 
        yaxis=dict(visible=False, showgrid=False, autorange=True, fixedrange=False),
        showlegend=False, 
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_rangeslider_visible=False,
        height=100
    )
    return fig

def render(df_swing):
    """
    Renders the Swing Trade analysis tab.
    df_swing: Swing trade data from Google Sheets (GID 1798886578)
    """
    if df_swing.empty:
        st.info("Sem dados de Swing Trade para exibir.")
        return

    st.markdown("## 📈 Análise e Operações: Swing Trade")
    
    # 1. Sector Logic & Alerts
    active_mask = (df_swing['Entrou'].str.upper() == 'SIM') & (df_swing['Resultado'].isin(['-', '', 'NAN', None]))
    analyzing_mask = (df_swing['Entrou'].str.upper() != 'SIM') & (df_swing['Resultado'].isin(['-', '', 'NAN', None]))
    
    # Get sectors for active and analyzing
    active_positions = df_swing[active_mask].copy()
    analyzing_positions = df_swing[analyzing_mask].copy()
    
    active_positions['Setor'] = active_positions['Ativo'].apply(get_sector)
    analyzing_positions['Setor'] = analyzing_positions['Ativo'].apply(get_sector)
    
    # Detailed Sector conflict alert
    all_current = pd.concat([active_positions, analyzing_positions])
    sector_groups = all_current.groupby('Setor')['Ativo'].apply(lambda x: sorted(list(set(x)))).to_dict()
    
    conflicts = {s: a for s, a in sector_groups.items() if len(a) > 1}
    
    if conflicts:
        with st.warning("⚠️ **Alerta de Concentração Setorial:**"):
            for sector, assets in conflicts.items():
                st.write(f"- **{sector}**: {', '.join(assets)}")
            st.caption("Evite sobreposição para gerenciar o risco sistêmico.")

    # 2. Priority View: Active Trades and Monitored Analyses
    st.markdown("### 🎯 Foco Principal: Acompanhando e Aberta")
    
    # Filter only for 'Acompanhando' or 'Aberta'
    status_filter = df_swing['Resultado'].str.strip().str.upper().isin(['ACOMPANHANDO', 'ABERTA'])
    latest_rows = df_swing[status_filter].copy()
    
    # Reverse to show most recent at top
    latest_rows = latest_rows.iloc[::-1]
    
    for idx, row in latest_rows.iterrows():
        status = row['Resultado'] if row['Resultado'] != '-' else 'EM ANÁLISE'
        with st.expander(f"{row['Ativo']} | {row['Periodo']} | Status: {status}", expanded=True):
            col1, col2, col3 = st.columns([1.5, 2, 3])
            with col1:
                st.metric("Ativo", row['Ativo'])
                st.caption(f"📅 {row['Data']}")
            with col2:
                # Metric combined with Mini-Graph
                st.write(f"**Tempo Gráfico:** {row['Periodo']}")
                # Fixed duplicate ID by adding a unique key based on Loop Index (row ID)
                st.plotly_chart(
                    render_sparkline(row['Ativo'], row['Periodo']), 
                    config={'displayModeBar': False}, 
                    use_container_width=True,
                    key=f"spark_{row['ID']}_{idx}"
                )
                st.write(f"**Lado:** {row['Extra1'] if pd.notna(row['Extra1']) else 'N/A'}")
            with col3:
                st.write("**📝 Observação Principal:**")
                st.info(row['Obs1'] if pd.notna(row['Obs1']) and row['Obs1'] != '-' else "Sem observações.")
                if pd.notna(row['Obs2']) and row['Obs2'] != '-':
                    st.write("**💡 Estratégia/Detalhe:**")
                    st.success(row['Obs2'])

    st.markdown("---")

    # 3. Market History
    st.markdown("### 📜 Histórico de Operações")
    
    # Show everything but formatted
    history_df = df_swing.iloc[::-1].copy() # Reverse
    history_df = history_df.rename(columns={
        'Data': 'Data',
        'Ativo': 'Ticker',
        'Periodo': 'Timeframe',
        'Entrou': 'Executou',
        'Resultado': 'Resultado (P/L)',
        'Obs1': 'Observação'
    })
    
    # Filter out empty/unexecuted only if they are old? 
    # User said: "vão sendo apagadas caso não tenham sido executadas" in the sheet, 
    # but in dashboard we just show what exists.
    
    st.dataframe(
        history_df[['Data', 'Ticker', 'Timeframe', 'Executou', 'Resultado (P/L)', 'Observação']],
        use_container_width=True,
        hide_index=True
    )

    # 4. Summary Stats (Optional but useful)
    with st.sidebar:
        st.markdown("---")
        st.markdown("### Swing Stats")
        total_trades = len(df_swing[df_swing['Resultado'] != '-'])
        gains = len(df_swing[df_swing['Resultado'].str.contains('GAIN', case=False, na=False)])
        losses = len(df_swing[df_swing['Resultado'].str.contains('LOSS', case=False, na=False)])
        
        if total_trades > 0:
            st.write(f"**Total Realizado:** {total_trades}")
            st.progress(gains/total_trades, text=f"Win Rate: {gains/total_trades:.1%}")
