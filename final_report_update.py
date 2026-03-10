import json
import os

path = r"g:\Meu Drive\Antigravity\Finançals Analysis (1)\data\relatorios.json"

# Final validated content based on the screenshot and user's confirmation
report_content = """# Relatório Semanal: 02/03 a 06/03
**Resultado Financeiro: R$ 2.476,00 (9 Operações)**

Esta semana demonstrou uma excelente recuperação e consistência, especialmente no uso de ordens limite em lateralidades e no aproveitamento de um rompimento de alta significativo.

> [!TIP]
> **O DIFERENCIAL DO R=500: SELETIVIDADE**
> Com 9 operações bem selecionadas, você atingiu um resultado robusto. A quarta e quinta-feira foram exemplares na execução técnica.

## 1. Performance por Tipo de Ordem
| Tipo de Ordem | Qtd | Lucro Total | Taxa de Acerto |
| :--- | :--- | :--- | :--- |
| **Ordem Limite** | 5 | R$ 1.500,00 | 60% |
| **Ordem Stop** | 4 | R$ 976,00 | 75% |

- **Destaque Técnico**: O lucro de **R$ 1.500,00** em uma única operação de Lateralidade (Limite) na quinta-feira mostra que você está colhendo os frutos de esperar o preço nos extremos do range.
- **Destaque Comportamental**: O Rompimento de Alta (Stop) de **R$ 1.000,00** na quarta-feira valida sua capacidade de entrar no modo *Always-In* quando o mercado apresenta urgência.

## 2. Análise de Setups (Top Profits)
1. **Lateralidade (Limite)**: R$ 1.500,00
2. **Rompimento de Alta (Stop)**: R$ 1.000,00
3. **Canal Estreito de Baixa (Stop)**: R$ 294,00

---

## 3. Avaliação Comportamental & Técnica
- **Resiliência**: Após um dia difícil na terça-feira (-R$ 534,00), você manteve a disciplina e não tentou "recuperar" no pânico. A paciência foi recompensada nos dias seguintes.
- **Transição de Contrato**: Mesmo com a mudança de contrato na sexta-feira, você manteve o controle, fechando o ciclo semanal no positivo.

---
### Meta para a Próxima Semana:
- Manter o foco absoluto nos extremos de lateralidades para ordens limite.
- Continuar aceitando a ordem stop apenas em rompimentos confirmados ou canais muito estreitos."""

new_report = {
    "id": 5,
    "title": "Relatório Semanal - 02/03 a 06/03",
    "date": "06/03/2026",
    "content": report_content
}

with open(path, 'r', encoding='utf-8') as f:
    reports = json.load(f)

# Update or add the report
found = False
for i, r in enumerate(reports):
    if r['id'] == 5:
        reports[i] = new_report
        found = True
        break

if not found:
    reports.append(new_report)

with open(path, 'w', encoding='utf-8') as f:
    json.dump(reports, f, indent=2, ensure_ascii=False)

print("Relatório semanal atualizado e validado para R$ 2.476,00!")
