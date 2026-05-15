"""
sync_day_trade.py
─────────────────
Lê os dados brutos da aba "Consolidado_Day_Trade" (Relatório de Performance do Profit)
e preenche automaticamente as colunas A-G da aba "OPERAÇÕES_DAY_TRADE".

Uso:
    python sync_day_trade.py            # Executa e escreve na planilha
    python sync_day_trade.py --dry-run  # Apenas mostra o que seria escrito
"""

import sys
import re
import requests
import io
import csv
import logging
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# ─── Config ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# The specific operation that acts as the anchor for the "new start"
CUTOFF_STR = "17/03/2026 10:57:12"
CUTOFF_DT = datetime.strptime(CUTOFF_STR, "%d/%m/%Y %H:%M:%S")

# Per user request: only modify lines BELOW row 95 (starting at row 96)
START_ROW = 96

SHEET_ID = "19FcL_LqH8AtyTlt2q2822XkayhpEgVWsKqUjPJxK1D4"
CREDS_FILE = r"G:\Meu Drive\Antigravity\Bitcoin\certs\google_creds.json"

# Published CSV URLs (read-only, no auth needed)
CONSOLIDADO_GID = "872600748"
OPERACOES_GID = "2017205813"
BASE_PUB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub"

CONSOLIDADO_URL = f"{BASE_PUB_URL}?gid={CONSOLIDADO_GID}&single=true&output=csv"
OPERACOES_URL = f"{BASE_PUB_URL}?gid={OPERACOES_GID}&single=true&output=csv"

# Target tab name in the spreadsheet (for gspread write)
TARGET_TAB = "OPERAÇÕES_DAY_TRADE"


# ─── Helpers ──────────────────────────────────────────────────────────────────
def fetch_csv(url: str) -> str:
    """Fetch raw CSV text from a published Google Sheets URL."""
    r = requests.get(url, headers={"Cache-Control": "no-cache"})
    r.raise_for_status()
    r.encoding = "utf-8"
    return r.text


def parse_consolidado(raw_csv: str) -> list[dict]:
    """
    Parse the messy Consolidado_Day_Trade CSV into clean operation records.
    
    The published CSV has semicolon-delimited Profit fields embedded inside
    comma-delimited cells. The approach: strip all double quotes, remove
    trailing empty comma-cells, then split by semicolons.
    
    Semicolon field layout (0-indexed):
        0: Ativo
        1: Abertura (date time)
        2: Fechamento (date time)
        3: Tempo Operação
        4: Qtd Compra
        5: Qtd Venda
        6: Lado (C/V)
        7-14: Preços, MEP, MEN, Agenciadores, Médio
       15: Res. Intervalo Bruto  ← col G
    """
    lines = raw_csv.splitlines()
    
    # Find the header line (contains "Ativo" and "Abertura")
    header_idx = -1
    for i, line in enumerate(lines[:20]):
        lower = line.lower()
        if "ativo" in lower and "abertura" in lower:
            header_idx = i
            break
    
    if header_idx == -1:
        logger.error("Header line not found in Consolidado CSV")
        return []
    
    operations = []
    
    for line in lines[header_idx + 1:]:
        line = line.strip()
        if not line:
            continue
        
        # Strip trailing empty CSV cells (,,,,,) and all double quotes
        cleaned = line.rstrip(",").replace('"', '')
        
        # Split by semicolons to get the actual Profit fields
        fields = [f.strip() for f in cleaned.split(";")]
        
        if len(fields) < 16:
            continue
        
        ativo = fields[0].strip().upper()
        
        # Skip non-ticker rows: must match B3 tickers (WIN, WDO, PETR4, BBSE3, etc.)
        if not ativo or not re.match(r'^[A-Z]{3,6}\d{0,3}$', ativo):
            continue
        
        abertura_raw = fields[1].strip()
        fechamento_raw = fields[2].strip()
        tempo = fields[3].strip()
        qtd_compra = fields[4].strip()
        qtd_venda = fields[5].strip()
        lado = fields[6].strip().upper()
        res_bruto_raw = fields[15].strip()
        
        # ── Clean Abertura/Fechamento ──
        # Source format: "17/03/2026,09:14:47" → target: "17/03/2026 09:14:47"
        abertura = abertura_raw.replace(",", " ").strip()
        fechamento = fechamento_raw.replace(",", " ").strip()
        
        # Validate we have date-like strings
        if not re.search(r'\d{2}/\d{2}/\d{4}', abertura):
            continue
        
        # ── Date Filtering ──
        try:
            op_dt = datetime.strptime(abertura, "%d/%m/%Y %H:%M:%S")
            if op_dt < CUTOFF_DT:
                continue
        except ValueError:
            logger.warning(f"Failed to parse date: {abertura}")
            continue
        
        # ── Clean Qtd ──
        # Use the maximum of Qtd Compra and Qtd Venda
        try:
            qc = int(qtd_compra) if qtd_compra.isdigit() else 0
            qv = int(qtd_venda) if qtd_venda.isdigit() else 0
            qtd = max(qc, qv)
        except ValueError:
            qtd = 0
        
        if qtd == 0:
            continue
        
        # ── Clean Lado ──
        if lado not in ("C", "V"):
            continue
        
        # ── Format Res. Bruto ──
        res_bruto = format_resultado(res_bruto_raw)
        
        operations.append({
            "Ativo": ativo,
            "Abertura": abertura,
            "Fechamento": fechamento,
            "Tempo": tempo,
            "Qtd": qtd,
            "Lado": lado,
            "Res. Bruto": res_bruto,
        })
    
    logger.info(f"Parsed {len(operations)} operations from Consolidado")
    return operations


def format_resultado(val: str) -> float:
    """
    Convert raw Profit result value to a float so Google Sheets 
    can apply number formats and conditional formatting correctly.
    """
    val = val.replace('"', '').replace("'", "").strip()
    
    if not val or val == "-":
        return 0.0
    
    # Detect negative
    negative = False
    if val.startswith("-"):
        negative = True
        val = val[1:]
    
    # Parse to float: "1.056,25" → "1056.25" → 1056.25
    clean = val.replace(".", "").replace(",", ".")
    try:
        num = float(clean)
        return -num if negative else num
    except ValueError:
        return 0.0



def get_existing_operations(raw_csv: str) -> set[str]:
    """
    Build a set of dedup keys from existing OPERAÇÕES_DAY_TRADE data.
    Key = "ATIVO|ABERTURA" to avoid inserting duplicates.
    """
    existing = set()
    lines = raw_csv.splitlines()
    if not lines:
        return existing
    
    # Read as CSV
    reader = csv.reader(io.StringIO(raw_csv))
    header = next(reader, None)
    if not header:
        return existing
    
    for row in reader:
        if len(row) < 2:
            continue
        ativo = row[0].strip().upper()
        abertura = row[1].strip()
        if ativo and abertura and re.search(r'\d', abertura):
            existing.add(f"{ativo}|{abertura}")
    
    logger.info(f"Found {len(existing)} existing operations in OPERAÇÕES_DAY_TRADE")
    return existing


def find_next_empty_row(worksheet) -> int:
    """Find the first empty row in column A (1-indexed)."""
    col_a = worksheet.col_values(1)
    # Filter out empty strings at the end
    while col_a and not col_a[-1].strip():
        col_a.pop()
    return len(col_a) + 1


def cleanup_target_sheet(worksheet, dry_run=False):
    """
    Clears everything starting from row START_ROW (96) to essentially 
    "restart" the sync from those rows.
    """
    logger.info(f"Cleaning up {TARGET_TAB} starting from row {START_ROW}...")
    
    # We first check if there are rows to clear
    col_a = worksheet.col_values(1)
    last_row = len(col_a)
    
    if last_row < START_ROW:
        logger.info("Nothing to clear (already empty after row 95).")
        return START_ROW
    
    clear_range = f"A{START_ROW}:G{last_row + 20}"
    logger.info(f"Clearing range: {clear_range}")
    
    if not dry_run:
        worksheet.batch_clear([clear_range])
    else:
        logger.info(f"[DRY-RUN] Would clear range {clear_range}")
        
    return START_ROW


def sync(dry_run: bool = False):
    """Main sync logic."""
    
    # 1. Fetch and parse source data
    logger.info("Authenticating with Google Sheets API...")
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SHEET_ID)
    
    logger.info(f"Fetching {TARGET_TAB} via gspread...")
    worksheet = spreadsheet.worksheet(TARGET_TAB) # This is OPERAÇÕES_DAY_TRADE
    consolidado_ws = spreadsheet.worksheet("Consolidado_Day_Trade")
    
    # Read all values from Consolidado to parse
    cons_data = consolidado_ws.get_all_values()
    
    # 2. Parse source data
    all_parsed_ops = []
    for row in cons_data:
        full_text = " ".join(row).replace('"', '')
        # Try splitting by ; first (Profit's standard)
        fields = [f.strip() for f in full_text.split(";")]
        
        if len(fields) < 16:
            # Try a different approach if not semicolon-separated
            tokens = re.split(r'[;,\s\t]+', full_text)
            # Find ticker and dates
            ativo = None
            for t in tokens:
                if re.match(r'^[A-Z]{3,6}\d{0,3}$', t.upper()):
                    ativo = t.upper()
                    break
            date_matches = re.findall(r'(\d{2}/\d{2}/\d{4})[,\s]*(\d{2}:\d{2}:\d{2})', full_text)
            if not ativo or not date_matches: continue
            
            abertura = f"{date_matches[0][0]} {date_matches[0][1]}"
            fechamento = f"{date_matches[1][0]} {date_matches[1][1]}" if len(date_matches) > 1 else ""
            
            op = {
                "Ativo": ativo,
                "Abertura": abertura,
                "Fechamento": fechamento,
                "Tempo": "",
                "Qtd": 0,
                "Lado": "",
                "Res. Bruto": 0.0
            }
        else:
            # Semicolon separated - but Profit sometimes splits date and time into fields[1] and [2]
            ativo = fields[0].upper()
            if not re.match(r'^[A-Z]{3,6}\d{0,3}$', ativo): continue
            
            f1 = fields[1].replace(",", " ").strip()
            f2 = fields[2].replace(",", " ").strip()
            
            # Case 1: f1 is "date time"
            if re.search(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}', f1):
                abertura = f1
                fechamento = f2
            # Case 2: f1 is "date" and f2 is "time"
            elif re.match(r'\d{2}/\d{2}/\d{4}', f1) and re.match(r'\d{2}:\d{2}:\d{2}', f2):
                abertura = f"{f1} {f2}"
                # Then Fechamento might be in fields[3] and [4]? No, usually Profit has a specific order.
                # Let's check fields[3] and [4]
                f3 = fields[3].replace(",", " ").strip()
                f4 = fields[4].replace(",", " ").strip()
                if re.match(r'\d{2}/\d{2}/\d{4}', f3) and re.match(r'\d{2}:\d{2}:\d{2}', f4):
                    fechamento = f"{f3} {f4}"
                    tempo = fields[5]
                    qtd = max(int(fields[6]) if fields[6].isdigit() else 0, int(fields[7]) if fields[7].isdigit() else 0)
                    lado = fields[8].upper()
                    res = format_resultado(fields[17]) # Shifted index
                else:
                    fechamento = ""
                    tempo = fields[3]
                    qtd = max(int(fields[4]) if fields[4].isdigit() else 0, int(fields[5]) if fields[5].isdigit() else 0)
                    lado = fields[6].upper()
                    res = format_resultado(fields[15])
            else:
                continue
            
            op = {
                "Ativo": ativo,
                "Abertura": abertura,
                "Fechamento": fechamento,
                "Tempo": tempo if 'tempo' in locals() else fields[3],
                "Qtd": qtd if 'qtd' in locals() else max(int(fields[4]) if fields[4].isdigit() else 0, int(fields[5]) if fields[5].isdigit() else 0),
                "Lado": lado if 'lado' in locals() else fields[6].upper(),
                "Res. Bruto": res if 'res' in locals() else format_resultado(fields[15]),
            }

        all_parsed_ops.append(op)
    
    logger.info(f"Parsed {len(all_parsed_ops)} operations from Consolidado")
    if all_parsed_ops:
        logger.info(f"Last parsed op Abertura: {all_parsed_ops[-1]['Abertura']}")
    
    # 3. Filter only operations STRICTLY AFTER the anchor
    new_ops = [op for op in all_parsed_ops if datetime.strptime(op["Abertura"], "%d/%m/%Y %H:%M:%S") > CUTOFF_DT]
    
    logger.info(f"Operations strictly after anchor: {len(new_ops)}")


    
    if not new_ops:
        logger.info("All operations already exist. Nothing to write.")
        return
    
    # ─── Find Next Empty Row ───
    # Instead of clearing, we find where the data currently ends in column A
    col_a = worksheet.col_values(1)
    # The last filled row
    last_filled = len(col_a)
    next_row = last_filled + 1
    
    if next_row < START_ROW:
        next_row = START_ROW
        
    logger.info(f"Targeting next empty row: {next_row}")

    # ─── Dedup Check ───
    # We only want to write trades that are NOT already in the sheet
    # We'll check the existing data in column B (Abertura) to avoid duplicates
    existing_dates = set(worksheet.col_values(2)) # Column B
    
    rows_to_write = []
    for op in new_ops:
        if op["Abertura"] in existing_dates:
            continue
            
        rows_to_write.append([
            op["Ativo"],           # A
            op["Abertura"],        # B
            op["Fechamento"],      # C
            op["Tempo"],           # D
            str(op["Qtd"]),        # E
            op["Lado"],            # F
            op["Res. Bruto"],      # G
        ])

    if not rows_to_write:
        logger.info("No new unique operations to write.")
        return

    logger.info(f"Writing {len(rows_to_write)} new rows starting at row {next_row}...")
    
    if not dry_run:
        # Batch update
        cell_range = f"A{next_row}:G{next_row + len(rows_to_write) - 1}"
        worksheet.update(rows_to_write, cell_range, value_input_option="USER_ENTERED")
        logger.info(f"✅ Successfully appended {len(rows_to_write)} new operations to {TARGET_TAB}!")
    else:
        logger.info(f"[DRY-RUN] Would append {len(rows_to_write)} rows starting at row {next_row}")



# ─── Entry Point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        logger.info("Running in DRY-RUN mode (no writes)")
    sync(dry_run=dry_run)
