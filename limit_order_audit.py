import pandas as pd
import numpy as np
import os
from datetime import datetime

# Configurações
BASE_DIR = r"g:\Meu Drive\Antigravity\Finançals Analysis (1)"
DT_FILE = os.path.join(BASE_DIR, "operacoes_dt.csv")
CONSOLIDADO_FILE = os.path.join(BASE_DIR, "consolidado.csv")

def clean_currency(val):
    if pd.isna(val) or str(val).strip() == '': return 0.0
    val_str = str(val).strip().replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
    try:
        return float(val_str)
    except:
        return 0.0

def run_audit():
    print("--- INICIANDO AUDITORIA DE ORDENS LIMITE ---")
    
    # Carregando Operações Day Trade
    try:
        df = pd.read_csv(DT_FILE)
    except Exception as e:
        print(f"Erro ao carregar {DT_FILE}: {e}")
        return

    # Limpeza básica
    df['Res. Bruto'] = df['Res. Bruto'].apply(clean_currency)
    df['Abertura'] = pd.to_datetime(df['Abertura'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Abertura']).sort_values('Abertura')

    # 1. Performance por Tipo de Ordem
    print("\n1. PERFORMANCE GERAL POR TIPO DE ORDEM:")
    stats = df.groupby('Tipo de Ordem')['Res. Bruto'].agg(['count', 'sum', 'mean']).reset_index()
    # Taxa de acerto
    wr = df.groupby('Tipo de Ordem').apply(lambda x: (x['Res. Bruto'] > 0).mean() * 100, include_groups=False).reset_index(name='WinRate_%')
    stats = stats.merge(wr, on='Tipo de Ordem')
    print(stats.to_string(index=False))

    # 2. Análise de Sequências de Perdas (Streaks)
    df['Is_Loss'] = df['Res. Bruto'] < 0
    df['Is_Limit'] = df['Tipo de Ordem'] == 'Ordem Limite'
    
    # Identificar sequências
    df['Streak_ID'] = (df['Is_Loss'] != df['Is_Loss'].shift()).cumsum()
    loss_streaks = df[df['Is_Loss']].groupby('Streak_ID').filter(lambda x: len(x) >= 2)
    
    print("\n2. ANÁLISE DE SEQUÊNCIAS DE PERDAS (2+ consecutivas):")
    if not loss_streaks.empty:
        summary_streaks = []
        for name, group in loss_streaks.groupby('Streak_ID'):
            first_op = group.iloc[0]
            triggered_by_limit = first_op['Is_Limit']
            total_loss = group['Res. Bruto'].sum()
            num_ops = len(group)
            summary_streaks.append({
                'Data': first_op['Abertura'].strftime('%d/%m/%Y %H:%M'),
                'Ops': num_ops,
                'Total_Perda': total_loss,
                'Iniciada_por_Limite': "SIM" if triggered_by_limit else "NÃO"
            })
        
        df_streaks = pd.DataFrame(summary_streaks)
        print(df_streaks.to_string(index=False))
        
        perc_limit_trigger = (df_streaks['Iniciada_por_Limite'] == "SIM").mean() * 100
        print(f"\nPorcentagem de sequências de perda iniciadas por Ordens Limite: {perc_limit_trigger:.1f}%")
    else:
        print("Nenhuma sequência de 2+ perdas encontrada nos dados.")

    # 3. Análise do "Efeito Cascata" (Cascade Effect)
    # Analisamos as N operações seguintes a qualquer ordem limite
    print("\n3. ANÁLISE DO EFEITO CASCATA (Impacto após QUALQUER Ordem Limite):")
    
    df['Follows_Limit'] = df['Tipo de Ordem'].shift() == 'Ordem Limite'
    df['Follows_Limit_Outcome'] = df['Res. Bruto'].shift().apply(lambda x: 'Win' if x > 0 else ('Loss' if x < 0 else 'BE'))
    
    cascade_analysis = df[df['Follows_Limit']].copy()
    
    if not cascade_analysis.empty:
        cascade_stats = cascade_analysis.groupby('Follows_Limit_Outcome')['Res. Bruto'].agg(['count', 'sum', 'mean']).reset_index()
        # Taxa de acerto após limite
        wr_cascade = cascade_analysis.groupby('Follows_Limit_Outcome').apply(lambda x: (x['Res. Bruto'] > 0).mean() * 100, include_groups=False).reset_index(name='WinRate_After_%')
        cascade_stats = cascade_stats.merge(wr_cascade, on='Follows_Limit_Outcome')
        
        print(cascade_stats.to_string(index=False))
        
        avg_wr_after_limit = (cascade_analysis['Res. Bruto'] > 0).mean() * 100
        avg_wr_total = (df['Res. Bruto'] > 0).mean() * 100
        
        print(f"\nTaxa de Acerto Geral: {avg_wr_total:.1f}%")
        print(f"Taxa de Acerto logo após Ordem Limite: {avg_wr_after_limit:.1f}%")
        
        if avg_wr_after_limit < avg_wr_total:
            print("\nINDICADOR: Há uma queda na performance logo após o uso de ordens limite.")
    else:
        print("Dados insuficientes para análise de cascata.")

    # 4. Detecção de "Pressão Psicológica" (Timing e Setup)
    print("\n4. DETECÇÃO DE PRESSÃO PSICOLÓGICA:")
    # Intervalo entre operações após QUALQUER ordem limite
    df['Time_Diff'] = df['Abertura'].diff().dt.total_seconds() / 60.0 # minutos
    
    pressure_cases = df[df['Follows_Limit'] & (df['Time_Diff'] < 20)]
    
    if not pressure_cases.empty:
        print(f"Detectadas {len(pressure_cases)} operações em menos de 20min após uma Ordem Limite.")
        print(pressure_cases[['Abertura', 'Ativo', 'Res. Bruto', 'Tipo de Ordem', 'SETUP Operado', 'Time_Diff']].to_string(index=False))
    else:
        print("Nenhum sinal óbvio de pressa/impaciência detectado após ordens limite.")

    # 5. Análise Mensal (Últimos 2 Meses)
    print("\n5. COMPARAÇÃO MENSAL:")
    df['Mes'] = df['Abertura'].dt.strftime('%Y-%m')
    mensal_stats = df.groupby(['Mes', 'Tipo de Ordem'])['Res. Bruto'].agg(['count', 'sum', 'mean']).reset_index()
    print(mensal_stats.to_string(index=False))

    # 6. Detalhadamento do "Efeito Cascata" por Desfecho da Ordem Limite
    print("\n6. TAXA DE ACERTO APÓS ORDEM LIMITE (POR RESULTADO):")
    # Já temos Follows_Limit_Outcome e a análise de cascata no passo 3.
    # Vamos apenas garantir que os dados de 2 meses apareçam.
    if not cascade_analysis.empty:
        # Re-calculando com mais dados se necessário
        print(cascade_stats.to_string(index=False))

if __name__ == "__main__":
    run_audit()

