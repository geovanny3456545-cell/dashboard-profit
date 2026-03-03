import streamlit as st
import pandas as pd
import numpy as np

def render():
    st.header("💎 Estratégias com Opções")
    st.markdown("""
    Esta aba permite simular e registrar operações com derivativos para proteção ou rentabilização da carteira.
    """)

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
                tempo_alvo = st.number_input("Barras até o Alvo (Tempo)", min_value=1, value=10, help="Quantas barras você espera que leve para atingir o alvo?")
                vencimento_opcoes = st.selectbox("Série de Vencimento", ["Próximo (Corrente)", "Seguinte"])

    st.markdown("---")
    
    # --- Seção de Escolha da Estrutura ---
    st.subheader("🛠️ Escolha da Estrutura de Opções")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        lado = st.radio("Direção do Trade", ["Alta (Compra de Calls)", "Baixa (Compra de Puts)"], horizontal=False)
        strike = st.number_input("Strike da Opção", min_value=0.01, value=31.00, step=0.1)

    with col2:
        tipo_estratégia = st.selectbox("Estrutura Sugerida", ["Compra Seca (Puro Delta)", "Trava de Alta/Baixa (Spread)", "Calendário (Time spread)"])
        premio_pago = st.number_input("Prêmio da Opção (Custo)", min_value=0.01, value=0.40, step=0.05)

    with col3:
        st.info(f"**Análise Brooks:**\n\nCiclo: {ciclo}\nSetup: {sinal}")
        if confianca_pa > 70:
            st.success("Setup de Alta Probabilidade.")
        else:
            st.warning("Setup de Probabilidade Moderada.")

    # --- Assistente de Estratégia ---
    st.subheader("💡 Assistente de Estratégia (Expert Advisor)")
    
    # Lógica de Recomendação Brooks
    with st.container():
        # Caso de ALTA
        if "Alta" in lado:
            if alvo_ativo <= preco_atual:
                st.error("⚠️ Erro: Alvo de ALTA abaixo do preço atual.")
            else:
                if ciclo == "Rompimento (Spike)" or ciclo == "Canal de Alta Estreito":
                    st.success("**Estratégia: Compra Seca de CALL (ITM)**")
                    st.write("Em rompimentos fortes ou canais estreitos, a urgência é alta. A compra seca captura o Delta rapidamente.")
                elif ciclo == "Trading Range":
                    st.info("**Estratégia: Venda de PUT (Lançamento Coberto)** ou **Trava de Alta**")
                    st.write("Em Trading Range, buscamos comprar baixo. Uma trava de alta perto do suporte é mais eficiente.")
                else:
                    if confianca_pa > 70:
                        st.success("**Estratégia: Compra de CALL (ATM)**")
                    else:
                        st.warning("**Estratégia: Trava de Alta (Bull Call Spread)**")
                        st.write("Baixa confiança ou canal amplo sugere proteção. A trava reduz o custo e o risco do tempo.")

        # Caso de BAIXA
        else:
            if alvo_ativo >= preco_atual:
                st.error("⚠️ Erro: Alvo de BAIXA acima do preço atual.")
            else:
                if ciclo == "Rompimento (Spike)" or ciclo == "Canal de Baixa Estreito":
                    st.success("**Estratégia: Compra Seca de PUT (ITM/ATM)**")
                else:
                    st.warning("**Estratégia: Trava de Baixa (Bear Put Spread)**")
                    st.write("Canais amplos de baixa costumam ter repiques. O spread protege melhor seu capital.")

    # --- Cálculos de Viabilidade ---
    distancia_alvo = abs((alvo_ativo / preco_atual) - 1) * 100
    intrinsic_value_at_target = max(0, alvo_ativo - strike) if "Alta" in lado else max(0, strike - alvo_ativo)
    potencial_lucro = (intrinsic_value_at_target / premio_pago - 1) * 100 if premio_pago > 0 else 0

    st.markdown("---")
    st.subheader("📊 Números da Operação")
    m1, m2, m3, m4 = st.columns(4)
    
    m1.metric("Distância Alvo", f"{distancia_alvo:.2f}%")
    m2.metric("V. Intrínseco no Alvo", f"R$ {intrinsic_value_at_target:.2f}")
    
    if potencial_lucro > 0:
        m3.metric("Potencial Lucro", f"{potencial_lucro:.0f}%")
    else:
        m3.metric("Potencial Lucro", "0%", delta="-100%", delta_color="inverse")
        
    prob_final = "Alta" if (confianca_pa > 70 and distancia_alvo < 5) else ("Baixa" if distancia_alvo > 10 else "Média")
    m4.metric("Probabilidade Final", prob_final)

    # --- Explicação Didática ---
    with st.expander("📚 Dicas de Price Action para Opções"):
        st.write("""
        1. **Rompimentos (Spikes)**: Geralmente têm alta probabilidade. Aceite pagar um prêmio mais caro em opções ITM (dentro do dinheiro) para não ficar fora do movimento.
        2. **Trading Range**: Não compre opções no meio do range. O decaimento do tempo (Theta) vai te destruir. Prefira vender opções nas extremidades ou usar travas.
        3. **Canais Amplos**: O movimento é lento. Opções secas sofrem com o tempo. Estruturas como **Spreads** são fundamentais aqui.
        4. **Theta & Brooks**: Se seu setup de Price Action prevê uma lateralidade por 10 barras, não compre opções curtas! O tempo vai corroer o prêmio antes do alvo ser atingido.
        """)

    # --- Listagem de Opções de Interesse (Exemplo) ---
    st.subheader("🔍 Monitoramento de Gregas (Beta)")
    st.info("Em breve: Integração com dados em tempo real para cálculo de Delta, Gamma e Theta.")

if __name__ == "__main__":
    render()
