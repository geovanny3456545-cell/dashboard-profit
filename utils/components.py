import streamlit as st

def glass_card(title, value, subtitle="", label_class="", extra_style=""):
    """
    Renders a premium glassmorphism metric card.
    """
    card_html = f"""
    <div class="glass-card">
        <label class="glass-label">{title}</label>
        <div class="glass-value {label_class}" style="{extra_style}">{value}</div>
        <div class="glass-subtitle">{subtitle}</div>
    </div>
    """
    return card_html

def status_badge(text, variant="default"):
    """
    Renders a stylized status badge.
    variants: default, success, danger, warning, info
    """
    colors = {
        "default": ("#444", "#eee"),
        "success": ("rgba(0, 250, 154, 0.15)", "#00fa9a"),
        "danger": ("rgba(255, 77, 77, 0.15)", "#ff4d4d"),
        "warning": ("rgba(255, 165, 0, 0.15)", "#ffa500"),
        "info": ("rgba(0, 170, 255, 0.15)", "#00aaff")
    }
    bg, fg = colors.get(variant, colors["default"])
    
    badge_html = f"""
    <span style="
        background-color: {bg};
        color: {fg};
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75em;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border: 1px solid {fg}33;
        display: inline-block;
        margin-right: 5px;
    ">{text}</span>
    """
    return badge_html

def section_header(title, icon=""):
    """Renders a modern section header with an optional icon."""
    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 20px;
        padding-bottom: 8px;
        border-bottom: 2px solid rgba(0, 170, 255, 0.3);
    ">
        <span style="font-size: 1.5em;">{icon}</span>
        <h2 style="margin: 0; font-size: 1.2em; letter-spacing: 1px; color: #00aaff; text-transform: uppercase;">
            {title}
        </h2>
    </div>
    """, unsafe_allow_html=True)

def error_boundary_container(title="Erro ao carregar componente"):
    """Renders a placeholder when a component fails."""
    st.markdown(f"""
    <div style="
        background: rgba(255, 77, 77, 0.05);
        border: 1px dashed rgba(255, 77, 77, 0.3);
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        color: #ff4d4d;
        font-size: 0.9em;
    ">
        ⚠️ {title}
    </div>
    """, unsafe_allow_html=True)
