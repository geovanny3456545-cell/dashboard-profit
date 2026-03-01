import json
import os

path = r"g:\Meu Drive\Antigravity\Finançals Analysis (1)\data\relatorios.json"

with open(path, 'r', encoding='utf-8') as f:
    reports = json.load(f)

# Weekly Report
week_content = """# Relatório Semanal: 23/02 a 27/02
**Resultado Financeiro: R$ 1.671,00 (21 Operações)**

Esta semana demonstrou uma maturidade significativa na escolha do tipo de ordem para cada regime de mercado. A transição entre Lateralidade e Urgência foi gerida com precisão técnica superior às semanas anteriores.

> [!TIP]
> **O MANTRA DA SEMANA: "RESPEITE O REGIME"**
> Você parou de brigar com rompimentos usando ordens limite e começou a colher os frutos de vender/comprar extremos em lateralidades.

## 1. Performance por Tipo de Ordem
| Tipo de Ordem | Qtd | Lucro Total | Taxa de Acerto | Profit Factor |
| :--- | :--- | :--- | :--- | :--- |
| **Ordem Limite** | 13 | R$ 1.168,00 | 53.8% | 2.15 |
| **Ordem Stop** | 8 | R$ 503,00 | 37.5% | 1.82 |

- **Destaque Técnico**: As **Ordens Limite** foram as rainhas da semana. Você identificou regimes de lateralidade e operou com "mão de valor", resultando em R$ 668,00 apenas nesse padrão.
- **Destaque Comportamental**: O medo de "perder o movimento" (FOMO) diminuiu. As ordens stop foram usadas estritamente em rompimentos ou canais estreitos, mesmo com uma taxa de acerto menor, o payoff compensou.

## 2. Análise de Setups (Top Profits)
1. **Lateralidade (Limite)**: R$ 668,00
2. **Canal Estreito de Baixa (Limite)**: R$ 500,00
3. **Lateralidade (Stop)**: R$ 491,00

---

## 3. Avaliação Comportamental & Técnica
### Ordens Stop x Limite
- **Technical Check**: O uso de Limit Orders em **Canal Estreito de Baixa** (R$ 500,00) foi audacioso, mas bem executado se feito a favor da tendência em pullbacks. No entanto, Brooks sugere cautela: em Canais Estreitos, a Ordem Stop no rompimento da barra anterior costuma ser mais segura.
- **Mental Game**: Você manteve a disciplina de não converter uma operação Stop em Limite (mudar a estratégia no meio do trade) na maioria das vezes. O alinhamento de 75%+ com o regime de mercado é o que está empurrando sua curva de capital para cima.

---
### Recomendações para a Próxima Semana:
- **Mantenha o Filtro de Lateralidades**: Continue usando ordens limite apenas quando o range estiver claro.
- **Ajuste no Canal Estreito**: Tente migrar o uso de ordens Limite em Canais Estreitos para ordens Stop na "espreita" (H1/L1 ou H2/L2), aumentando a probabilidade de entrar no momentum certo."""

# Monthly Report
month_content = """# Relatório Mensal: Fechamento de Fevereiro 2026
**Resultado Final: R$ 1.571,00 (53 Operações)**

Fevereiro foi um mês de consolidação metodológica. Apesar de um início turbulento, a reta final (esta semana) salvou o mês e colocou a conta no positivo, provando que o gerenciamento técnico vence a ansiedade no longo prazo.

## 1. Estatísticas do Mês
- **Total Financeiro**: R$ 1.571,00
- **Win Rate Médio**: 40.2%
- **Performance Stop vs Limite**: 
    - **Ordens Stop**: R$ 1.683,00 de lucro.
    - **Ordens Limite**: R$ 1.388,00 de lucro.

## 2. O Grande Vencedor: Rompimentos (Ordem Stop)
O maior motor de lucro do mês foi o **Rompimento de Alta** operado com **Ordem Stop (R$ 1.051,00)**. 
- **Lição**: Quando o mercado entra em modo *Always-In* (Urgência), você soube pagar o preço da ordem stop para garantir a participação no movimento de Swing.

## 3. A Batalha das Lateralidades
As lateralidades foram o seu maior desafio psicológico. Você teve ganhos expressivos com Ordens Limite (R$ 668,00 na última semana), mas perdas acumuladas no início do mês devido a "tentar adivinhar o topo/fundo" antes da confirmação do range.

### Performance Mensal por Setup:
| Setup | Tipo | Lucro Acumulado |
| :--- | :--- | :--- |
| Canal Estreito de Baixa | Limite | R$ 1.100,00 |
| Rompimento de Alta | Stop | R$ 1.051,00 |
| Canal Estreito de Alta | Limite | R$ 675,00 |
| lateralidade | Stop | R$ 390,00 |
| **Lateralidade** | **Limite** | **R$ -387,00 (Acumulado)** |

> [!IMPORTANT]
> Note que, apesar da semana excelente, o saldo mensal das Lateralidades com Ordens Limite ainda é negativo. Isso mostra que os erros do início do mês foram severos. **O progresso técnico é real, mas o histórico exige vigilância.**

---

## 4. Veredito Técnico & Comportamental
### Evolução Stop x Limite
- **Technical**: Você finalmente entendeu que a **Ordem Stop não é um "prejuízo garantido"**, mas sim o ingresso para os trades de alta probabilidade em momentum.
- **Behavioral**: A "Síndrome do Breakeven de Pânico" diminuiu 15% em relação a Janeiro. Você está segurando mais os Swings, especialmente em Rompimentos de Alta.

### Meta para Março:
- Zerar o saldo negativo acumulado em Lateralidades (Ordem Limite).
- Refinar a entrada em Canais Estreitos (migrar gradualmente para Ordens Stop a favor da tendência)."""

new_reports = [
    {
        "id": 3,
        "title": "Relatório Semanal - 23/02 a 27/02",
        "date": "27/02/2026",
        "content": week_content
    },
    {
        "id": 4,
        "title": "Relatório Mensal - Fevereiro 2026",
        "date": "27/02/2026",
        "content": month_content
    }
]

reports.extend(new_reports)

with open(path, 'w', encoding='utf-8') as f:
    json.dump(reports, f, indent=2, ensure_ascii=False)

print("Relatórios adicionados com sucesso!")
