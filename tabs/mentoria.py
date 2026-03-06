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

    # Layout Styles
    st.markdown("""
    <style>
    /* Simplied fonts to avoid fetch issues */
    .mentorship-card {
        background: #1e2327;
        border-left: 6px solid #00aaff;
        padding: 30px;
        border-radius: 12px;
        margin-bottom: 30px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .mentorship-header {
        color: #00aaff;
        font-size: 1.6em;
        font-weight: 700;
        margin-bottom: 20px;
    }
    .main-text {
        color: #e0e6ed;
        line-height: 1.6;
        font-size: 1.05em;
        margin-bottom: 25px;
    }
    .rule-box {
        background: rgba(0, 170, 255, 0.05);
        border: 1px solid rgba(0, 170, 255, 0.1);
        border-radius: 8px;
        padding: 20px;
    }
    .rule-box-title {
        font-weight: 700;
        color: #fff;
        margin-bottom: 15px;
        text-transform: uppercase;
        font-size: 0.85em;
        letter-spacing: 1.5px;
    }
    .rule-item {
        margin-bottom: 12px;
        display: flex;
        align-items: flex-start;
    }
    .rule-bullet {
        color: #00aaff;
        margin-right: 12px;
        font-weight: 700;
        flex-shrink: 0;
    }
    .rule-content {
        color: #cdd9e5;
    }
    .highlight-gold { color: #ffd700; }
    </style>
    """, unsafe_allow_html=True)

    # Rendering the Card
    rules_html = ""
    rules_list = data.get("rules", [])
    if isinstance(rules_list, list):
        for rule in rules_list:
            if isinstance(rule, dict):
                r_id = rule.get('id', '?')
                r_title = rule.get('title', 'Sem Título')
                r_content = rule.get('content', '')
                # Fix markdown bold replacement
                r_content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', r_content)
                rules_html += f"""
                <div style="margin-bottom: 20px; display: flex; align-items: flex-start;">
                    <span style="color: #00aaff; font-weight: bold; margin-right: 12px; font-size: 1.1em;">{r_id})</span>
                    <span style="color: #cdd9e5; line-height: 1.5;"><b>{r_title}:</b> {r_content}</span>
                </div>
                """

    html_content = f"""
    <div style="background: #1e2327; border-left: 6px solid #00aaff; padding: 30px; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); font-family: sans-serif;">
        <div style="color: #00aaff; font-size: 1.6em; font-weight: 700; margin-bottom: 20px;">
            {data.get('title', 'Mentoria')}
        </div>
        <div style="color: #e0e6ed; line-height: 1.6; font-size: 1.05em; margin-bottom: 25px;">
            {data.get('main_text', '')}
        </div>
        
        <div style="background: rgba(0, 170, 255, 0.05); border: 1px solid rgba(0, 170, 255, 0.1); border-radius: 8px; padding: 25px;">
            <div style="font-weight: 700; color: #fff; margin-bottom: 20px; text-transform: uppercase; font-size: 0.85em; letter-spacing: 1.5px;">
                🛡️ Regras de Ouro (Pregão Diário)
            </div>
            {rules_html}
        </div>
        
        <div style="margin-top: 30px; padding: 20px; background: rgba(0, 170, 255, 0.05); border-radius: 10px; font-style: italic; color: #a0aec0; text-align: center; line-height: 1.6;">
            {data.get('quote', '')}
        </div>
        
        <div style="font-size: 9px; color: #444; margin-top: 25px; text-align: right; opacity: 0.5;">
            v2.2-stable | Sync OK
        </div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)
    
    if data.get("footer_success"):
        st.success(data.get("footer_success"))
