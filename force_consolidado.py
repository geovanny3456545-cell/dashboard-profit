import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SHEET_ID = "14iTFjqHSKFPdLT9rieop6lFozA9ZkC_zYmfjjjV7HlU"
CREDS_FILE = r"G:\Meu Drive\Antigravity\Bitcoin\certs\google_creds.json"

def force_consolidado():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(SHEET_ID)
        
        try:
            sheet = spreadsheet.worksheet("Consolidado")
            logger.info("Aba Consolidado já existe.")
        except gspread.exceptions.WorksheetNotFound:
            logger.info("Aba Consolidado não encontrada. Criando agora...")
            sheet = spreadsheet.add_worksheet(title="Consolidado", rows="1000", cols="9")
            headers = ["Dia", "Hora", "Usuário", "Descrição", "Categoria", "Prioridade", "Pagamento", "Valor", "Mês_Ref"]
            sheet.append_row(headers)
            logger.info("Aba Consolidado criada com sucesso!")
            
        worksheets = [ws.title for ws in spreadsheet.worksheets()]
        logger.info(f"Abas atuais na planilha: {worksheets}")
            
    except Exception as e:
        logger.error(f"Erro ao forçar aba: {e}")

if __name__ == "__main__":
    force_consolidado()
