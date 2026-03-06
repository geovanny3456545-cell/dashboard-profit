import streamlit as st
import pandas as pd

def render(df, metrics):
    if df.empty:
        st.info("Sem dados para exibir no momento.")
        return

    # Unpack metrics
    total_pnl = metrics['total_pnl']
    gross_profit = metrics['gross_profit']
    gross_loss = metrics['gross_loss']
    num_trades = metrics['num_trades']
    win_rate = metrics['win_rate']
    profit_factor = metrics['profit_factor']
    avg_pnl = metrics['avg_pnl']
    avg_win = metrics['avg_win']
    avg_loss = metrics['avg_loss']
    payoff = metrics['payoff']
    max_win = metrics['max_win']
    max_loss = metrics['max_loss']
    max_w_streak = metrics['max_w_streak']
    max_l_streak = metrics['max_l_streak']
    max_dd = metrics['max_dd']

    # --- TAB: RESUMO (Legacy Nelogica Layout) ---
    # Top Headline Stats
    h1, h2, h3 = st.columns([2, 5, 2])
    with h2: 
        lbl_col = "profit-val" if total_pnl >= 0 else "loss-val"
        st.markdown(f"<div style='text-align:center; font-size:2.5em; margin-bottom:10px;' class='{lbl_col}'>R$ {total_pnl:,.2f}</div>", unsafe_allow_html=True)
        st.markdown("<div style='text-align:center; color:#888; margin-top:-15px;'>Resultado Total</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Grid Layout
    def grid_row(label, value, value_class="", extra_style=""):
        return f"""
        <div class='grid-row'>
            <span class='grid-label'>{label}</span>
            <span class='grid-value {value_class}' style='{extra_style}'>{value}</span>
        </div>
        """

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("<div class='grid-header'>Estatísticas Principais</div>", unsafe_allow_html=True)
        st.markdown(grid_row("Lucro Bruto", f"R$ {gross_profit:,.2f}", "profit-val"), unsafe_allow_html=True)
        st.markdown(grid_row("Prejuízo Bruto", f"R$ {gross_loss:,.2f}", "loss-val"), unsafe_allow_html=True)
        st.markdown(grid_row("Fator de Lucro", f"{profit_factor:.2f}"), unsafe_allow_html=True)
        st.markdown(grid_row("Total de Trades", f"{num_trades}"), unsafe_allow_html=True)
        st.markdown(grid_row("Taxa de Acerto", f"{win_rate:.2f}%", "profit-val", extra_style="color:#00fa9a !important;"), unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='grid-header'>Médias</div>", unsafe_allow_html=True)
        st.markdown(grid_row("Média Lucro/Prejuízo", f"R$ {avg_pnl:,.2f}", "profit-val" if avg_pnl > 0 else "loss-val"), unsafe_allow_html=True)
        st.markdown(grid_row("Média de Ganho", f"R$ {avg_win:,.2f}", "profit-val"), unsafe_allow_html=True)
        st.markdown(grid_row("Média de Perda", f"R$ {avg_loss:,.2f}", "loss-val"), unsafe_allow_html=True)
        st.markdown(grid_row("Payoff", f"{payoff:.2f}"), unsafe_allow_html=True)

    with c3:
        st.markdown("<div class='grid-header'>Extremos</div>", unsafe_allow_html=True)
        st.markdown(grid_row("Maior Ganho", f"R$ {max_win:,.2f}", "profit-val"), unsafe_allow_html=True)
        st.markdown(grid_row("Maior Perda", f"R$ {max_loss:,.2f}", "loss-val"), unsafe_allow_html=True)
        st.markdown(grid_row("Drawdown Máximo", f"R$ {max_dd:,.2f}", "loss-val"), unsafe_allow_html=True)
        st.markdown(grid_row("Seq. Vencedora", f"{max_w_streak}", "profit-val"), unsafe_allow_html=True)
        st.markdown(grid_row("Seq. Perdedora", f"{max_l_streak}", "loss-val"), unsafe_allow_html=True)
        
        st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
        st.markdown("<div class='grid-header'>Monitor de Disciplina (Substack)</div>", unsafe_allow_html=True)
        streak = metrics.get('discipline_streak', 0)
        st.markdown(grid_row("Trades sem Fading", f"{streak} 🔥", "profit-val" if streak > 5 else ""), unsafe_allow_html=True)
