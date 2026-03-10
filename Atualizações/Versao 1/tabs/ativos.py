import streamlit as st
import pandas as pd
import plotly.express as px

def render(df):
    """
    Renders the Results by Asset chart.
    df: filtered data for current view
    """
    if df.empty:
        st.info("Sem dados para exibir na aba Ativos.")
        return

    st.markdown("### Resultados por Ativo")
    
    # Calculate performance by asset
    # Assuming 'Ativo' is the column name (standardized in data_loader)
    asset_col = 'Ativo'
    if asset_col not in df.columns:
        # Fallback to finding it in columns if not standardized
        asset_cols = [c for c in df.columns if 'ativo' in c.lower()]
        asset_col = asset_cols[0] if asset_cols else None

    if asset_col:
        asset_stats = df.groupby(asset_col).agg({
            'Res_Numeric': 'sum'
        }).reset_index()
        
        asset_stats = asset_stats.sort_values('Res_Numeric', ascending=False)
        
        # Determine colors for bars
        asset_stats['Color'] = asset_stats['Res_Numeric'].apply(lambda x: '#00fa9a' if x > 0 else '#ff4d4d' if x < 0 else '#bbbbbb')

        fig = px.bar(
            asset_stats, 
            x=asset_col, 
            y='Res_Numeric',
            color='Color',
            color_discrete_map={'#00fa9a': '#00fa9a', '#ff4d4d': '#ff4d4d', '#bbbbbb': '#bbbbbb'},
            title="Lucro/Prejuízo por Ativo (R$)"
        )
        
        fig.update_layout(
            plot_bgcolor='#1e1e1e', 
            paper_bgcolor='#1e1e1e', 
            font=dict(color='#ddd'),
            xaxis_title="Ativo",
            yaxis_title="Resultado (R$)",
            coloraxis_showscale=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Optional: Add a small table with metrics
        st.markdown("---")
        st.markdown("#### Detalhamento por Ativo")
        
        detail_stats = df.groupby(asset_col).agg({
            'Res_Numeric': ['sum', 'count', lambda x: (x > 0).sum() / len(x) * 100]
        }).reset_index()
        
        detail_stats.columns = ['Ativo', 'Resultado Total', 'Qtd Trades', 'Win Rate (%)']
        detail_stats['Resultado Total'] = detail_stats['Resultado Total'].map('R$ {:,.2f}'.format)
        detail_stats['Win Rate (%)'] = detail_stats['Win Rate (%)'].map('{:.1f}%'.format)
        
        st.table(detail_stats)
    else:
        st.warning("Coluna de Ativo não encontrada nos dados.")
