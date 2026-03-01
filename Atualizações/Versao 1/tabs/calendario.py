import streamlit as st
import pandas as pd
import datetime
import calendar
from utils import notes_manager as nm
from utils import b3_calendar as b3

def render(df_raw, selected_asset="Todos"):
    # Initialize Session State
    if 'cal_date' not in st.session_state:
        st.session_state['cal_date'] = datetime.date.today().replace(day=1)
    if 'note_editor_date' not in st.session_state:
        st.session_state['note_editor_date'] = None

    if df_raw.empty:
        st.info("Sem dados para o calendário.")
        return
    
    # 1. Navigation & State Setup
    curr_dt = st.session_state['cal_date']
    cal_year = curr_dt.year
    cal_month = curr_dt.month
    
    # Header: Prev | Month Year | Next
    kp1, kp2, kp3 = st.columns([1, 6, 1])
    
    if kp1.button("◀ Anterior", key="cal_prev"):
        first = curr_dt.replace(day=1)
        prev_month = first - datetime.timedelta(days=1)
        st.session_state['cal_date'] = prev_month.replace(day=1)
        st.rerun()
        
    with kp2:
        month_label = calendar.month_name[cal_month].upper()
        months_pt = {
            1: "JANEIRO", 2: "FEVEREIRO", 3: "MARÇO", 4: "ABRIL", 5: "MAIO", 6: "JUNHO",
            7: "JULHO", 8: "AGOSTO", 9: "SETEMBRO", 10: "OUTUBRO", 11: "NOVEMBRO", 12: "DEZEMBRO"
        }
        month_label = months_pt.get(cal_month, month_label)
        st.markdown(f"<h2 style='text-align: center; margin: 0;'>{month_label} {cal_year}</h2>", unsafe_allow_html=True)
        
    if kp3.button("Próximo ▶", key="cal_next"):
        _, days_in_month = calendar.monthrange(cal_year, cal_month)
        next_month = curr_dt.replace(day=1) + datetime.timedelta(days=days_in_month + 1)
        st.session_state['cal_date'] = next_month.replace(day=1)
        st.rerun()

    st.markdown("---")

    # 2. Note Editor (Overlay)
    if st.session_state['note_editor_date']:
        edit_dt = st.session_state['note_editor_date']
        st.info(f"📝 Editando nota para: **{edit_dt.strftime('%d/%m/%Y')}**")
        curr_note = nm.get_note_for_date(edit_dt)
        with st.form(key="note_form"):
            new_text = st.text_area("Conteúdo da Nota:", value=curr_note, height=100)
            c_save, c_cancel = st.columns([1, 1])
            if c_save.form_submit_button("Salvar Nota"):
                nm.save_note_for_date(edit_dt, new_text)
                st.session_state['note_editor_date'] = None
                st.rerun()
            if c_cancel.form_submit_button("Cancelar"):
                st.session_state['note_editor_date'] = None
                st.rerun()
        st.markdown("---")

    # 3. Data Preparation
    _, num_days = calendar.monthrange(cal_year, cal_month)
    m_start = datetime.date(cal_year, cal_month, 1)
    m_end = datetime.date(cal_year, cal_month, num_days)
    
    df_cal = df_raw[(df_raw['Date'] >= m_start) & (df_raw['Date'] <= m_end)].copy()
    if selected_asset != "Todos": 
        if 'Ativo' in df_cal.columns:
            df_cal = df_cal[df_cal['Ativo'] == selected_asset]
    
    # Monthly Summary
    if not df_cal.empty:
        tot_res = df_cal['Res_Numeric'].sum()
        gross_gain = df_cal[df_cal['Res_Numeric'] > 0]['Res_Numeric'].sum()
        gross_loss = df_cal[df_cal['Res_Numeric'] < 0]['Res_Numeric'].sum()
        st.markdown(f"""
        <div style="display: flex; justify-content: center; gap: 40px; margin-bottom: 20px;">
            <div style="text-align: center;">
                <p style="margin:0; font-size: 0.85em; color: #888;">Resultado Líquido</p>
                <p style="margin:0; font-size: 1.3em; font-weight: bold; color: {'#00fa9a' if tot_res > 0 else '#ff4d4d' if tot_res < 0 else '#bbbbbb'}">R$ {tot_res:,.2f}</p>
            </div>
            <div style="text-align: center;">
                <p style="margin:0; font-size: 0.85em; color: #888;">Lucro Bruto</p>
                <p style="margin:0; font-size: 1.3em; font-weight: bold; color: #00fa9a">R$ {gross_gain:,.2f}</p>
            </div>
            <div style="text-align: center;">
                <p style="margin:0; font-size: 0.85em; color: #888;">Prejuízo Bruto</p>
                <p style="margin:0; font-size: 1.3em; font-weight: bold; color: #ff4d4d">R$ {gross_loss:,.2f}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    daily_res = df_cal.groupby('Date')['Res_Numeric'].sum().to_dict()
    daily_details = {}
    if not df_cal.empty:
        for d, x in df_cal.groupby('Date'):
            details = []
            for _, row in x.iterrows():
                t_str = str(row['Abertura']).replace('"', '').replace("'", "") if pd.notnull(row['Abertura']) else "?"
                res_val = row['Res_Numeric']
                res_s = f"R$ {res_val:,.2f}"
                details.append(f"{t_str} | {res_s}")
            daily_details[d] = "&#10;".join(details)

    # 4. Calendar Grid
    calendar.setfirstweekday(6)
    month_matrix = calendar.monthcalendar(cal_year, cal_month)
    cols = st.columns(7)
    days_header = ["DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SÁB"]
    for i, day_name in enumerate(days_header):
        cols[i].markdown(f"<p style='text-align:center; color:#888; font-size:0.8em; margin:0;'>{day_name}</p>", unsafe_allow_html=True)
        
    for week in month_matrix:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.container(height=80, border=False)
                else:
                    this_dt = datetime.date(cal_year, cal_month, day)
                    val = daily_res.get(this_dt, 0.0)
                    has_data = this_dt in daily_res
                    is_trading = b3.is_trading_day(this_dt)
                    note = nm.get_note_for_date(this_dt)
                    has_note = len(note.strip()) > 0
                    
                    tooltip_text = f"Dia {day}/{cal_month}"
                    if has_data:
                        tooltip_text += f"\nSaldo: R$ {val:,.2f}\n---\n{daily_details.get(this_dt, '')}"
                    if has_note:
                        tooltip_text += f"\n\nNota: {note}"
                    t_safe = tooltip_text.replace('"', "'").replace('<', '').replace('>', '')
                    
                    with st.container(border=True):
                        if has_data:
                            color = "#00fa9a" if val > 0 else "#ff4d4d" if val < 0 else "#bbbbbb"
                            html_day = f"""
                            <div title="{t_safe}" style="cursor: help; text-align: center; height: 60px;">
                                <span style="color: #888; font-weight: bold; font-size: 1.2em; display: block; margin-bottom: 5px;">{day}</span>
                                <span style="color: {color}; font-size: 0.9em; font-weight: bold; display: block;">R$ {val:,.2f}</span>
                            </div>
                            """
                            st.markdown(html_day, unsafe_allow_html=True)
                        elif not is_trading:
                            # Non-trading day dash
                            st.markdown(f"""
                            <div style='text-align: center; height: 60px;'>
                                <span style='color: #888; font-size: 1.2em; display: block; margin-bottom: 5px;'>{day}</span>
                                <span style='color: #444; font-size: 1.2em; display: block;'>—</span>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style='text-align: center; height: 60px;'>
                                <span style='color: #888; font-size: 1.2em; display: block; margin-bottom: 5px;'>{day}</span>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        if has_note: st.caption("📝 Nota")
                        else: st.caption(" ")
