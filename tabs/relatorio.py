import streamlit as st
import json
import os

def render():
    st.title("📑 Relatórios de Performance")
    st.markdown("---")
    
    # Path to reports
    reports_path = os.path.join("data", "relatorios.json")
    
    if not os.path.exists(reports_path):
        st.warning("Nenhum relatório encontrado.")
        return
        
    try:
        with open(reports_path, 'r', encoding='utf-8') as f:
            reports = json.load(f)
    except Exception as e:
        st.error(f"Erro ao carregar relatórios: {e}")
        return
        
    if not reports:
        st.info("A fileira de relatórios está vazia.")
        return
        
    # Reverse reports to show newest first
    reports_display = reports[::-1]
    
    # Selector
    options = [f"{r['title']} ({r['date']})" for r in reports_display]
    selected_option = st.selectbox("Selecione o Relatório:", options)
    
    # Get selected report index
    selected_idx = options.index(selected_option)
    report = reports_display[selected_idx]
    
    # Display Content
    st.markdown(f"### {report['title']}")
    st.caption(f"📅 Data: {report['date']}")
    st.markdown("---")
    
    st.markdown(report['content'], unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Substack Export Feature
    with st.expander("📥 Exportar para Substack"):
        st.write("Copie o código abaixo e cole no seu post do Substack:")
        substack_md = f"""# {report['title']}
> Data: {report['date']}

{report['content']}

---
*Análise gerada automaticamente pelo Dashboard de Performance Al Brooks.*
"""
        st.code(substack_md, language="markdown")
    
    st.info("💡 Este relatório é fixo e não é afetado pelos filtros de data globais do dashboard.")
