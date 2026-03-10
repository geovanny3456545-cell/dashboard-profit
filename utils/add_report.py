import json
import os

def append_report():
    reports_path = os.path.join("data", "relatorios.json")
    md_path = "relatorio_riscos_wdo.md"
    
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    if os.path.exists(reports_path):
        with open(reports_path, "r", encoding="utf-8") as f:
            reports = json.load(f)
    else:
        reports = []
        
    new_id = max([r['id'] for r in reports], default=0) + 1
    
    new_report = {
        "id": new_id,
        "title": "WDO: Erradicação de Riscos e Mesas Proprietárias",
        "date": "23/02/2026",
        "content": content
    }
    
    reports.append(new_report)
    
    with open(reports_path, "w", encoding="utf-8") as f:
        json.dump(reports, f, indent=2, ensure_ascii=False)
    print(f"Relatório {new_id} adicionado com sucesso.")

if __name__ == "__main__":
    append_report()
