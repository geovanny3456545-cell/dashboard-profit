import json
import os

path = r"g:\Meu Drive\Antigravity\Finançals Analysis (1)\data\relatorios.json"

report_content = """# Relatório Semanal: 02/03 a 06/03
**Resultado Financeiro: R$ 1.950,00 (11 Operações)**

Esta semana foi marcada por grandes acertos em operações de valor (Lateralidade) e um excelente aproveitamento de um rompimento de alta na quarta-feira. O lucro de R$ 1.500,00 na quinta-feira em uma lateralidade foi o ponto alto técnico da semana.

> [!TIP]
> **INSIGHT DA SEMANA: SELETIVIDADE NO R=500**
> Você mostrou que consegue segurar alvos maiores em lateralidades claras. O lucro médio por operação vencedora subiu consideravelmente.

## 1. Performance por Tipo de Ordem
| Tipo de Ordem | Qtd | Lucro Total | Status |
| :--- | :--- | :--- | :--- |
| **Ordem Limite** | 5 | R$ 1.500,00 | **Excelente (Foco em TR)** |
| **Ordem Stop** | 4 | R$ 976,00 | **Sólido (Rompimentos)** |
| **Outros/Messy** | 2 | R$ -526,00 | **Atenção (Sexta-feira)** |

- **Destaque Técnico**: A operação de **R$ 1.500,00** (05/03) em Lateralidade com Ordem Limite mostra que você está respeitando os extremos do range com confiança.
- **Destaque Comportamental**: O Rompimento de Alta de **R$ 1.000,00** (04/03) operado com Ordem Stop prova que você parou de brigar com o momentum forte.

## 2. Análise de Setups (Top Profits)
1. **Lateralidade (Limite)**: R$ 1.500,00 (Quinta-feira)
2. **Rompimento de Alta (Stop)**: R$ 1.000,00 (Quarta-feira)
3. **Canal Estreito de Baixa (Stop)**: R$ 294,00

---

## 3. Avaliação Técnica
- **Sexta-feira (06/03)**: Foi o dia mais desafiador, com um prejuízo acumulado de ~R$ 526,00 no final da manhã. A transição para o novo contrato (WINJ26) pode ter trazido uma volatilidade diferente da habitual.
- **Consistência**: Apesar do dia negativo na terça (-R$ 534,00 em rompimento de baixa), a recuperação na quarta e quinta foi tecnicamente perfeita, mantendo o gerenciamento de risco.

---
### Recomendações para a Próxima Semana:
- **Atenção à Sexta**: Analise se houve fadiga emocional ou técnica nas operações de hoje.
- **Confiança na TR**: O setup de lateralidade está sendo sua mina de ouro; continue operando apenas os extremos confirmados."""

new_report = {
    "id": 5,
    "title": "Relatório Semanal - 02/03 a 06/03",
    "date": "06/03/2026",
    "content": report_content
}

with open(path, 'r', encoding='utf-8') as f:
    reports = json.load(f)

# Avoid duplicates
if not any(r['id'] == 5 for r in reports):
    reports.append(new_report)

with open(path, 'w', encoding='utf-8') as f:
    json.dump(reports, f, indent=2, ensure_ascii=False)

print("Relatório semanal adicionado com sucesso!")
