import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SHEET_ID = "14iTFjqHSKFPdLT9rieop6lFozA9ZkC_zYmfjjjV7HlU"
CREDS_FILE = r"G:\Meu Drive\Antigravity\Bitcoin\certs\google_creds.json"

def consolidate_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(SHEET_ID)
        
        all_data = []
        worksheets = spreadsheet.worksheets()
        
        for ws in worksheets:
            if ws.title != "Consolidado" and "-" in ws.title: # Filtra abas mensais ex: 03-2026
                logger.info(f"Lendo dados da aba: {ws.title}")
                data = ws.get_all_records()
                if data:
                    df = pd.DataFrame(data)
                    df['Mês_Ref'] = ws.title # Adiciona referência do mês
                    all_data.append(df)
        
        if not all_data:
            logger.info("Nenhuma aba mensal com dados encontrada.")
            return
            
        consolidated_df = pd.concat(all_data, ignore_index=True)
        
        # Criar ou atualizar aba Consolidado
        try:
            consolidated_ws = spreadsheet.worksheet("Consolidado")
            spreadsheet.del_worksheet(consolidated_ws)
            logger.info("Aba Consolidado existente removida para atualização.")
        except gspread.exceptions.WorksheetNotFound:
            pass
            
        consolidated_ws = spreadsheet.add_worksheet(title="Consolidado", rows=str(len(consolidated_df) + 100), cols=str(len(consolidated_df.columns)))
        
        # Preparar dados para upload (incluindo cabeçalho)
        rows = [consolidated_df.columns.tolist()] + consolidated_df.fillna("").values.tolist()
        consolidated_ws.update('A1', rows)
        
        logger.info(f"Consolidação concluída com sucesso! {len(consolidated_df)} registros processados.")
            
    except Exception as e:
        logger.error(f"Erro na consolidação: {e}")

if __name__ == "__main__":
    consolidate_sheets()
