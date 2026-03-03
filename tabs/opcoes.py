import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

# --- Persistence Utils ---
DB_PATH = "data/opcoes.json"

def load_saved_strategies():
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_strategies(strategies):
    # Ensure directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(strategies, f, indent=4, ensure_ascii=False)

def get_b3_expiration(year, month):
    """Calculates the 3rd Friday of a given month/year."""
    first_day = datetime(year, month, 1)
    first_friday = (4 - first_day.weekday() + 7) % 7
    third_friday = 1 + first_friday + 14
    return datetime(year, month, third_friday)

def get_series_info(target_date, is_call=True):
    """Returns the series letter and month name for B3 options."""
    month = target_date.month
    call_letters = "ABCDEFGHIJKL"
    put_letters = "MNOPQRSTUVWX"
    letter = call_letters[month-1] if is_call else put_letters[month-1]
    month_names = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    return letter, month_names[month-1]

def render():
    st.header("💎 Estratégias com Opções")
    
    # Initialize strategies in session state if not present
    if "saved_strategies" not in st.session_state:
        st.session_state.saved_strategies = load_saved_strategies()

    # --- Seção de Entrada de Dados ---
    with st.expander("📝 Nova Simulação de Opção (Foco em Price Action Brooks)", expanded=True):
        col_pa, col_entry = st.columns([1, 1])
        
        with col_pa:
            st.subheader("🕵️ Contexto Brooks")
            ciclo = st.selectbox("Ciclo de Mercado", ["Canal de Alta Estreito", "Canal de Alta Amplo", "Trading Range", "Canal de Baixa Amplo", "Canal de Baixa Estreito", "Rompimento (Spike)"])
            sinal = st.selectbox("Barra de Sinal/Setup", ["H1/L1", "H2/L2", "Barra de Reversão", "Bandeira de Rompimento", "MTR (Major Trend Reversal)", "Test of Extreme"])
            confianca_pa = st.slider("Confiança no Setup (%)", 0, 100, 60)

        with col_entry:
            st.subheader("🎯 Alvos e Prazos")
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                preco_atual = st.number_input("Preço da Ação (R$)", min_value=0.01, value=30.00, step=0.1)
                alvo_ativo = st.number_input("Alvo (Brooks Target)", min_value=0.01, value=33.00, step=0.1)
            with col_e2:
                tempo_alvo = st.number_input("Barras até o Alvo (Tempo/Dias)", min_value=1, value=10)
                
                # --- Cálculo Automático de Vencimento ---
                today = datetime.now()
                # Simplified: assuming 1 bar = 1 calendar day for expiration check
                target_date_est = today + pd.Timedelta(days=tempo_alvo)
                
                cur_exp = get_b3_expiration(today.year, today.month)
                if target_date_est > cur_exp:
                    # Suggest next month if target is after current expiration
                    suggested_exp = get_b3_expiration(target_date_est.year, target_date_est.month)
                else:
                    suggested_exp = cur_exp
                
                st.caption(f"💡 Sugestão: Vencimento em {suggested_exp.strftime('%d/%m/%Y')}")

    st.markdown("---")
    
    # --- Seção de Escolha da Estrutura ---
    st.subheader("🛠️ Escolha da Estrutura de Opções")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        lado = st.radio("Direção do Trade", ["Alta (Compra de Calls)", "Baixa (Compra de Puts)"], horizontal=False)
        is_call = "Alta" in lado
        letter, month_name = get_series_info(suggested_exp, is_call)
        
        ativo_objeto = st.text_input("Código do Ativo (ex: PETR4)", value="PETR4").upper()
        
        # Auto-suggest Ticker
        default_ticker = f"{ativo_objeto[:4]}{letter}{int(preco_atual)}" if len(ativo_objeto) >= 4 else ""
        opcao_ticker = st.text_input("Código da Opção (Sugerido)", value=default_ticker).upper()
        st.caption(f"Série **{letter}** ({month_name}) indicada pelo sistema.")

    with col2:
        strike = st.number_input("Strike da Opção", min_value=0.01, value=float(int(preco_atual + 1)), step=0.1)
        tipo_estratégia = st.selectbox("Estrutura Sugerida", ["Compra Seca (Puro Delta)", "Trava de Alta/Baixa (Spread)", "Calendário (Time spread)"])
        premio_pago = st.number_input("Prêmio pago (Custo)", min_value=0.01, value=0.40, step=0.05)

    with col3:
        st.info(f"**Análise Brooks:**\n\nCiclo: {ciclo}\nSetup: {sinal}")
        if confianca_pa > 70:
            st.success("Setup de Alta Probabilidade.")
        else:
            st.warning("Setup de Probabilidade Moderada.")

    # --- Assistente de Estratégia ---
    st.subheader("💡 Assistente de Estratégia (Expert Advisor)")
    
    with st.container():
        # Lógica de Recomendação (Simplificada)
        recomp_text = ""
        if "Alta" in lado:
            if alvo_ativo <= preco_atual:
                st.error("⚠️ Erro: Alvo de ALTA abaixo do preço atual.")
            else:
                if ciclo == "Rompimento (Spike)" or ciclo == "Canal de Alta Estreito":
                    recomp_text = "Compra Seca de CALL (ITM)"
                    st.success(f"**Estratégia: {recomp_text}**")
                else:
                    recomp_text = "Trava de Alta"
                    st.info(f"**Estratégia: {recomp_text}**")
        else:
            if alvo_ativo >= preco_atual:
                st.error("⚠️ Erro: Alvo de BAIXA acima do preço atual.")
            else:
                recomp_text = "Compra de PUT ou Trava"
                st.success(f"**Estratégia: {recomp_text}**")

    # --- Cálculos de Viabilidade ---
    distancia_alvo = abs((alvo_ativo / preco_atual) - 1) * 100
    intrinsic_value_at_target = max(0, alvo_ativo - strike) if "Alta" in lado else max(0, strike - alvo_ativo)
    potencial_lucro = (intrinsic_value_at_target / premio_pago - 1) * 100 if premio_pago > 0 else 0

    st.markdown("---")
    st.subheader("📊 Números da Operação")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Distância Alvo", f"{distancia_alvo:.2f}%")
    m2.metric("V. Intrínseco no Alvo", f"R$ {intrinsic_value_at_target:.2f}")
    m3.metric("Potencial Lucro", f"{potencial_lucro:.0f}%")
    prob_final = "Alta" if (confianca_pa > 70 and distancia_alvo < 5) else ("Baixa" if distancia_alvo > 10 else "Média")
    m4.metric("Probabilidade Final", prob_final)

    # --- Botão Salvar ---
    if st.button("💾 Salvar Estratégia nos Cards"):
        new_strat = {
            "id": str(datetime.now().timestamp()),
            "data_entrada": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "ativo": ativo_objeto,
            "opcao": opcao_ticker,
            "lado": lado,
            "ciclo": ciclo,
            "sinal": sinal,
            "strike": strike,
            "alvo": alvo_ativo,
            "potencial": f"{potencial_lucro:.0f}%",
            "prob": prob_final
        }
        st.session_state.saved_strategies.insert(0, new_strat)
        save_strategies(st.session_state.saved_strategies)
        st.success("Estratégia salva com sucesso!")
        st.rerun()

    # --- Exibição dos Cards ---
    st.markdown("---")
    st.subheader("🗂️ Suas Estratégias Salvas")
    
    if not st.session_state.saved_strategies:
        st.info("Nenhuma estratégia salva ainda.")
    else:
        for idx, strat in enumerate(st.session_state.saved_strategies):
            with st.container():
                # Grid para o Card
                c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
                
                with c1:
                    st.markdown(f"**{strat['ativo']}** - `{strat['opcao']}`")
                    st.caption(f"🗓️ Entrada: {strat['data_entrada']}")
                
                with c2:
                    st.write(f"🎯 Alvo: R$ {strat['alvo']:.2f}")
                    st.write(f"📈 Potencial: {strat['potencial']}")
                
                with c3:
                    st.write(f"🧠 {strat['ciclo']}")
                    st.write(f"🎲 Prob: {strat['prob']}")
                
                with c4:
                    if st.button("🗑️", key=f"del_{strat['id']}"):
                        st.session_state.saved_strategies.pop(idx)
                        save_strategies(st.session_state.saved_strategies)
                        st.rerun()
                
                st.markdown("<hr style='margin:5px 0; border:0.5px solid #444'>", unsafe_allow_html=True)

    # --- Explicação Didática ---
    with st.expander("📚 Dicas de Price Action para Opções"):
        st.write("""
        1. **Rompimentos (Spikes)**: Geralmente têm alta probabilidade. Aceite pagar um prêmio mais caro em opções ITM (dentro do dinheiro) para não ficar fora do movimento.
        2. **Trading Range**: Não compre opções no meio do range. O decaimento do tempo (Theta) vai te destruir. Prefira vender opções nas extremidades ou usar travas.
        3. **Canais Amplos**: O movimento é lento. Opções secas sofrem com o tempo. Estruturas como **Spreads** são fundamentais aqui.
        4. **Theta & Brooks**: Se seu setup de Price Action prevê uma lateralidade por 10 barras, não compre opções curtas! O tempo vai corroer o prêmio antes do alvo ser atingido.
        """)
