import streamlit as st
import json
import os

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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Outfit:wght@500;700&display=swap');
    
    .mentorship-card {
        background: linear-gradient(145deg, #161a1d 0%, #1e2327 100%);
        border: 1px solid rgba(0, 170, 255, 0.1);
        border-left: 6px solid #00aaff;
        padding: 35px;
        border-radius: 16px;
        margin-bottom: 30px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        font-family: 'Inter', sans-serif;
    }
    .mentorship-header {
        font-family: 'Outfit', sans-serif;
        color: #00aaff;
        font-size: 1.8em;
        font-weight: 700;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        letter-spacing: -0.5px;
        text-shadow: 0 0 20px rgba(0, 170, 255, 0.2);
    }
    .main-text {
        color: #e0e6ed;
        line-height: 1.7;
        font-size: 1.1em;
        margin-bottom: 30px;
        padding-bottom: 20px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    .rule-box {
        background: rgba(0, 170, 255, 0.03);
        backdrop-filter: blur(5px);
        border: 1px solid rgba(0, 170, 255, 0.1);
        border-radius: 12px;
        padding: 25px;
        margin-top: 20px;
    }
    .rule-box-title {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        color: #fff;
        margin-bottom: 20px;
        text-transform: uppercase;
        font-size: 0.9em;
        letter-spacing: 2px;
        display: flex;
        align-items: center;
        opacity: 0.9;
    }
    .rule-item {
        margin-bottom: 18px;
        display: flex;
        align-items: flex-start;
        transition: transform 0.2s ease;
    }
    .rule-item:hover {
        transform: translateX(5px);
    }
    .rule-bullet {
        color: #00aaff;
        margin-right: 15px;
        font-weight: 700;
        font-size: 1.2em;
        background: rgba(0, 170, 255, 0.1);
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        flex-shrink: 0;
    }
    .rule-content {
        color: #cdd9e5;
    }
    .rule-content b {
        color: #ffffff;
        font-weight: 600;
    }
    .highlight-gold { 
        color: #ffd700; 
        font-weight: 700;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.2);
    }
    .quote-container {
        margin-top: 40px;
        padding: 20px;
        background: rgba(0, 170, 255, 0.05);
        border-radius: 10px;
        border-right: 3px solid rgba(0, 170, 255, 0.2);
    }
    .quote-text {
        font-family: 'Inter', sans-serif;
        font-style: italic;
        color: #a0aec0;
        font-size: 1.05em;
        text-align: center;
        line-height: 1.6;
    }
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
                # Adicionar destaque automático para termos em negrito ou destaque
                r_content = r_content.replace("**", "<b>").replace("**", "</b>")
                rules_html += f"""
                <div class="rule-item">
                    <div class="rule-bullet">{r_id}</div>
                    <div class="rule-content"><b>{r_title}:</b> {r_content}</div>
                </div>
                """

    html_content = f"""
    <div class="mentorship-card">
        <div class="mentorship-header">
            {data.get('title', 'Mentoria')}
        </div>
        <div class="main-text">
            {data.get('main_text', '')}
        </div>
        
        <div class="rule-box">
            <div class="rule-box-title">
                <span style="margin-right:10px">🛡️</span> Regras de Ouro (Pregão Diário)
            </div>
            {rules_html}
        </div>
        
        <div class="quote-container">
            <div class="quote-text">
                {data.get('quote', '')}
            </div>
        </div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)
    
    if data.get("footer_success"):
        st.success(data.get("footer_success"))
