import json
import os

path = r"g:\Meu Drive\Antigravity\Finançals Analysis (1)\data\relatorios.json"

report_content = """# Relatórios Semanal: 02/03/2026 a 06/03/2026
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

---

## 2. A Grande Mudança: O Pivô do 2:1
Após analisarmos a volatilidade da sexta-feira e a pressão psicológica de alvos longos, decidimos por um ajuste estratégico vital: **Focar em alvos de 2:1 em vez de 3:1.**

- **Racional**: O 3:1 exige uma precisão e paciência que, em dias de transição de contrato ou alta volatilidade, podem causar "paralisia" ou erros de overtrading se o alvo não for atingido rapidamente.
- **Matemática**: Com sua taxa de acerto atual (>40%), o 2:1 é estatisticamente vencedor e psicologicamente muito mais fácil de gerir. Buscar R$ 1.000 para um risco de R$ 500 é o caminho para a consistência inabalável.

---

## 3. Avaliação Comportamental & Técnica
- **Resiliência**: Após um dia difícil na terça-feira (-R$ 534,00), você manteve a disciplina. A paciência foi recompensada nos dias seguintes.
- **Transição de Contrato**: Mesmo com a mudança para o WINJ26 na sexta-feira, o controle emocional foi mantido até o final, apesar da frustração com os alvos longos.

---
### Recomendações para a Próxima Semana:
- **Alvo Fixo 2:1**: Experimente realizar lucros no 2:1 de forma sistemática para construir "colchão" financeiro e confiança.
- **Mantenha o Foco na TR**: O setup de lateralidade continua sendo sua maior fonte de receita com ordens limite.
"""

new_report = {
    "id": 5,
    "title": "Relatório Semanal - 02/03 a 06/03",
    "date": "06/03/2026",
    "content": report_content
}

with open(path, 'r', encoding='utf-8') as f:
    reports = json.load(f)

for i, r in enumerate(reports):
    if r['id'] == 5:
        reports[i] = new_report
        break

with open(path, 'w', encoding='utf-8') as f:
    json.dump(reports, f, indent=2, ensure_ascii=False)

print("Relatórios atualizados com o pivô estratégico para 2:1.")
