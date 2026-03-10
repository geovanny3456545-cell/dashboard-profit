import streamlit as st
import json
import os
import re

def load_mentoria_data():
    file_path = os.path.join("data", "mentoria.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_mentoria_data(data):
    file_path = os.path.join("data", "mentoria.json")
    os.makedirs("data", exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def render():
    data = load_mentoria_data()
    
    # Sidebar control for editing
    edit_mode = st.sidebar.toggle("📝 Modo Edição (Mentoria)", value=False)
    
    if edit_mode:
        st.subheader("✏️ Editar Mentoria")
        with st.form("mentoria_edit_form"):
            new_title = st.text_input("Título", value=data.get("title", ""))
            new_main_text = st.text_area("Texto Principal", value=data.get("main_text", ""), height=100)
            
            st.divider()
            st.write("**Regras de Ouro**")
            new_rules = []
            for i, rule in enumerate(data.get("rules", [])):
                col1, col2 = st.columns([1, 3])
                with col1:
                    r_title = st.text_input(f"Título Regra {i+1}", value=rule.get("title", ""), key=f"title_{i}")
                with col2:
                    r_content = st.text_area(f"Conteúdo Regra {i+1}", value=rule.get("content", ""), key=f"content_{i}", height=70)
                new_rules.append({"id": i+1, "title": r_title, "content": r_content})
            
            st.divider()
            new_quote = st.text_input("Citação", value=data.get("quote", ""))
            new_footer = st.text_input("Rodapé (Sucesso)", value=data.get("footer_success", ""))
            
            if st.form_submit_button("Salvar Alterações"):
                data["title"] = new_title
                data["main_text"] = new_main_text
                data["rules"] = new_rules
                data["quote"] = new_quote
                data["footer_success"] = new_footer
                save_mentoria_data(data)
                st.success("Configurações salvas com sucesso!")
                st.rerun()

    # --- NATIVE STREAMLIT RENDERING (Ultra Stable) ---
    st.title(data.get('title', 'Mentoria'))
    
    st.info(data.get('main_text', ''))
    
    st.subheader("🛡️ Regras de Ouro (Pregão Diário)")
    
    rules_list = data.get("rules", [])
    if isinstance(rules_list, list):
        for rule in rules_list:
            if isinstance(rule, dict):
                r_id = rule.get('id', '?')
                r_title = rule.get('title', 'Sem Título')
                r_content = rule.get('content', '')
                
                with st.container(border=True):
                    # Use columns for the bullet and content
                    b_col, c_col = st.columns([0.1, 0.9])
                    with b_col:
                        st.write(f"### {r_id})")
                    with c_col:
                        st.markdown(f"**{r_title}:** {r_content}")

    st.divider()
    
    if data.get("quote"):
        st.markdown(f"> *{data.get('quote')}*")
    
    if data.get("footer_success"):
        st.success(data.get("footer_success"))
    
    st.caption("v2.3.0-native-stable")
