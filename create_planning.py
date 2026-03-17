import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SHEET_ID = "14iTFjqHSKFPdLT9rieop6lFozA9ZkC_zYmfjjjV7HlU"
CREDS_FILE = r"G:\Meu Drive\Antigravity\Bitcoin\certs\google_creds.json"

def create_planning_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(SHEET_ID)
        
        try:
            sheet = spreadsheet.worksheet("Planejamento")
            logger.info("Aba Planejamento já existe.")
        except gspread.exceptions.WorksheetNotFound:
            logger.info("Aba Planejamento não encontrada. Criando...")
            sheet = spreadsheet.add_worksheet(title="Planejamento", rows="100", cols="2")
            headers = ["Categoria", "Gasto Máximo Mensal"]
            # Exemplos de categorias comuns
            rows = [
                headers,
                ["Alimentação", 1000],
                ["Lazer", 500],
                ["Essencial", 2000],
                ["Transporte", 300],
                ["Saúde", 400]
            ]
            sheet.update('A1', rows)
            logger.info("Aba Planejamento criada com sucesso com exemplos!")
            
    except Exception as e:
        logger.error(f"Erro ao criar aba de planejamento: {e}")

if __name__ == "__main__":
    create_planning_sheet()
