import pandas as pd
import numpy as np
import os
import sys

# Handlig encoding for console output
sys.stdout.reconfigure(encoding='utf-8')

# Define absolute paths - UPDATED LOCATIONS
base_dir = r"g:\Meu Drive\Antigravity\Finançals Analysis"
data_file = os.path.join(base_dir, "trading_data_day_trade.csv")
report_file = os.path.join(base_dir, "trading_analysis_report.md")

try:
    if not os.path.exists(data_file):
        # Fallback to local if running in dev environment without G: drive access (unlikely per instructions)
        # But for robustness:
        print(f"File not found at {data_file}. Checking current dir.")
        if os.path.exists("trading_data_day_trade.csv"):
            data_file = "trading_data_day_trade.csv"
            report_file = "trading_analysis_report.md"

    df = pd.read_csv(data_file)
    
    # --- Data Cleaning ---
    df.columns = [c.replace('\n', ' ').strip() for c in df.columns]
    df['Abertura'] = pd.to_datetime(df['Abertura'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Abertura']) # Clean empty rows
    
    # Financials
    def clean_currency(val):
        if pd.isna(val) or val == '': return 0.0
        val_str = str(val).strip().replace('R$', '').replace(' ', '')
        if ',' in val_str and '.' in val_str: val_str = val_str.replace('.', '').replace(',', '.')
        elif ',' in val_str: val_str = val_str.replace(',', '.')
        try: return float(val_str)
        except: return 0.0
    
    df['Res_Numeric'] = df['Res. Bruto'].apply(clean_currency)
    
    def categorize_result(val):
        if val > 0: return 'Win'
        elif val < 0: return 'Loss'
        else: return 'Breakeven'
    df['Result_Type'] = df['Res_Numeric'].apply(categorize_result)
    
    # Extract Order Type - UPDATED
    if 'Tipo de Ordem' in df.columns:
        df['Order_Type_Raw'] = df['Tipo de Ordem'].fillna('Other').astype(str)
        # Standardize
        def clean_order_type(val):
            val_lower = val.lower()
            if 'limit' in val_lower: return 'Limit'
            if 'stop' in val_lower: return 'Stop'
            return val # Return as is if neither
        df['Order_Type'] = df['Order_Type_Raw'].apply(clean_order_type)
    else:
        # Fallback extraction
        def extract_order_type(val):
            val = str(val).replace('\n', ' ').lower()
            if 'stop' in val: return 'Stop'
            if 'limite' in val: return 'Limit'
            return 'Other'
        df['Order_Type'] = df['SETUP Operado'].apply(extract_order_type)
    
    # Extract Operado Setup Name
    def extract_setup_name(val):
        val = str(val).replace('\n', ' ')
        # Naive: try to strip common prefixes
        lower_val = val.lower()
        for prefix in ['ordem stop', 'ordem limite', 'venda limite', 'compra limite']:
            if lower_val.startswith(prefix):
                return val[len(prefix):].strip()
        return val.strip()
    df['Setup_Name_Operated'] = df['SETUP Operado'].apply(extract_setup_name)
    
    # Standardize 'Added' column
    def is_added(val):
        val_str = str(val).strip().lower()
        if val_str.startswith('n'):
            return 'No'
        return 'Yes'
    df['Position_Added'] = df['Adicionou'].apply(is_added)

    # Date/Time
    df['Hour'] = df['Abertura'].dt.hour
    
    # --- Analysis & Reporting ---
    
    lines = []
    lines.append("# Análise Estatística - Day Trade")
    lines.append(f"**Total de Operações Analisadas:** {len(df)}")
    lines.append("")
    
    # 1. Performance Overview
    lines.append("## 1. Visão Geral de Performance")
    win_counts = df['Result_Type'].value_counts()
    total = len(df)
    
    wins = win_counts.get('Win', 0)
    losses = win_counts.get('Loss', 0)
    breakeven = win_counts.get('Breakeven', 0)
    
    lines.append(f"- **Win Rate (Ganhos):** {wins} ({wins/total:.1%})")
    lines.append(f"- **Loss Rate (Perdas):** {losses} ({losses/total:.1%})")
    lines.append(f"- **Breakeven (Empates/0x0):** {breakeven} ({breakeven/total:.1%})")
    lines.append(f"- **Total Financeiro:** R$ {df['Res_Numeric'].sum():.2f}")
    lines.append("")

    # 2. Ordem Limit vs Stop
    lines.append("## 2. Tipo de Ordem (Limite vs Stop)")
    # Calculate stats manually to ensure we catch all categories
    order_types = df['Order_Type'].unique()
    lines.append("| Tipo de Ordem | Operações | Win % | Loss % | Breakeven % |")
    lines.append("|---|---|---|---|---|")
    
    for otype in sorted(order_types):
        subset = df[df['Order_Type'] == otype]
        count = len(subset)
        if count == 0: continue
        
        vc = subset['Result_Type'].value_counts(normalize=True)
        w = vc.get('Win', 0.0)
        l = vc.get('Loss', 0.0)
        be = vc.get('Breakeven', 0.0)
        
        lines.append(f"| {otype} | {count} | {w:.1%} | {l:.1%} | {be:.1%} |")
    lines.append("")
    
    # 3. Position Added
    lines.append("## 3. Aumentos de Posição (Adicionou)")
    
    lines.append("| Adicionou Posição? | Operações | Win % | Loss % | Breakeven % |")
    lines.append("|---|---|---|---|---|")
    for status in ['Yes', 'No']:
        subset = df[df['Position_Added'] == status]
        count = len(subset)
        if count == 0: continue
            
        vc = subset['Result_Type'].value_counts(normalize=True)
        w = vc.get('Win', 0.0)
        l = vc.get('Loss', 0.0)
        be = vc.get('Breakeven', 0.0)
        lines.append(f"| {status} | {count} | {w:.1%} | {l:.1%} | {be:.1%} |")
    lines.append("")
    
    # 4. Management Correctness
    lines.append("## 4. Gerenciamento Correto")
    if 'Gerenciou Corretamente?' in df.columns:
        mgt_col = 'Gerenciou Corretamente?'
        df[mgt_col] = df[mgt_col].fillna('-').astype(str)
        
        lines.append("| Gerenciou Corretamente? | Operações | Win % | Loss % | Breakeven % |")
        lines.append("|---|---|---|---|---|")
        
        # Sort manually: Sim, Não, -
        order = ['Sim', 'Não', '-']
        existing = df[mgt_col].unique()
        for x in existing:
            if x not in order: order.append(x)
            
        for status in order:
            if status not in existing: continue
            subset = df[df[mgt_col] == status]
            count = len(subset)
            vc = subset['Result_Type'].value_counts(normalize=True)
            w = vc.get('Win', 0.0)
            l = vc.get('Loss', 0.0)
            be = vc.get('Breakeven', 0.0)
            lines.append(f"| {status} | {count} | {w:.1%} | {l:.1%} | {be:.1%} |")
    lines.append("")

    # 5. Hand Size Correctness
    lines.append("## 5. Mão (Lote) Correta")
    if 'Mão correta?' in df.columns:
        hand_col = 'Mão correta?'
        df[hand_col] = df[hand_col].fillna('-').astype(str)
        
        lines.append("| Mão Correta? | Operações | Win % | Loss % | Breakeven % |")
        lines.append("|---|---|---|---|---|")
        
        existing = sorted(df[hand_col].unique(), reverse=True) 
        for status in existing:
            subset = df[df[hand_col] == status]
            count = len(subset)
            vc = subset['Result_Type'].value_counts(normalize=True)
            w = vc.get('Win', 0.0)
            l = vc.get('Loss', 0.0)
            be = vc.get('Breakeven', 0.0)
            lines.append(f"| {status} | {count} | {w:.1%} | {l:.1%} | {be:.1%} |")
    lines.append("")

    # 6. Time of Day
    lines.append("## 6. Melhor Horário")
    
    lines.append("| Hora | Operações | Win % | Loss % | Breakeven % |")
    lines.append("|---|---|---|---|---|")
    
    hours = sorted(df['Hour'].unique())
    for hour in hours:
        subset = df[df['Hour'] == hour]
        count = len(subset)
        vc = subset['Result_Type'].value_counts(normalize=True)
        w = vc.get('Win', 0.0)
        l = vc.get('Loss', 0.0)
        be = vc.get('Breakeven', 0.0)
        lines.append(f"| {int(hour)}h | {count} | {w:.1%} | {l:.1%} | {be:.1%} |")
    lines.append("")
    
    # 7. Setup Real vs Operated
    lines.append("## 7. Análise de Setups")
    
    # Win Rate per Operated Setup
    lines.append("### Top 10 Setups Operados")
    
    op_counts = df['Setup_Name_Operated'].value_counts()
    
    lines.append("| Setup Operado | Operações | Win % | Loss % | Breakeven % |")
    lines.append("|---|---|---|---|---|")
    # Sort by count desc
    for setup in op_counts.index[:10]: # Top 10
        subset = df[df['Setup_Name_Operated'] == setup]
        count = len(subset)
        vc = subset['Result_Type'].value_counts(normalize=True)
        w = vc.get('Win', 0.0)
        l = vc.get('Loss', 0.0)
        be = vc.get('Breakeven', 0.0)
        lines.append(f"| {setup} | {count} | {w:.1%} | {l:.1%} | {be:.1%} |")
        
    lines.append("")
    lines.append("### Setup Operado vs Setup Real (Consistência)")
    def matches_setup(row):
        op = str(row['Setup_Name_Operated']).lower().strip()
        real = str(row['SETUP Real']).lower().strip()
        
        ignore = ['ordem', 'limite', 'stop', 'compra', 'venda', '\n', '  ']
        for x in ignore:
            op = op.replace(x, '')
            real = real.replace(x, '')
        
        op = op.replace('rompimentode', 'rompimento').replace('canalestreitode', 'canalestreito')
        real = real.replace('rompimentode', 'rompimento').replace('canalestreitode', 'canalestreito')
        
        op_words = set([w for w in op.split() if w])
        real_words = set([w for w in real.split() if w])
        
        if not op_words or not real_words: return False
        
        intersection = op_words.intersection(real_words)
        return len(intersection) > 0 
    
    df['Setup_Match'] = df.apply(matches_setup, axis=1)
    match_count = df['Setup_Match'].sum()
    
    lines.append(f"- **Concordância (Setup Real x Operado):** {match_count}/{total} ({match_count/total:.1%})")
    
    # 8. Extra insights
    lines.append("")
    lines.append("## 8. Outros  Indicadores")
    # Best streak? Worst streak?
    # Ordered by date
    df = df.sort_values(by='Abertura')
    
    current_streak = 0
    max_win_streak = 0
    max_loss_streak = 0
    current_type = None
    
    for res in df['Result_Type']:
        if res == 'Win':
            if current_type == 'Win':
                current_streak += 1
            else:
                current_streak = 1
                current_type = 'Win'
            max_win_streak = max(max_win_streak, current_streak)
        elif res == 'Loss':
            if current_type == 'Loss':
                current_streak += 1
            else:
                current_streak = 1
                current_type = 'Loss'
            max_loss_streak = max(max_loss_streak, current_streak)
        else:
            current_streak = 0
            current_type = None
            
    lines.append(f"- **Maior Sequência de Ganhos:** {max_win_streak}")
    lines.append(f"- **Maior Sequência de Perdas:** {max_loss_streak}")
    
    
    # Write Report
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"Report generated at: {report_file}")

except Exception as e:
    print(f"Analysis Failed: {e}")
    import traceback
    traceback.print_exc()
