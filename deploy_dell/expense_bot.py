import logging
import pandas as pd
from datetime import datetime
from telegram import Update
import json
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, JobQueue
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import asyncio

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configurações via Variáveis de Ambiente ou Padrão Local
TOKEN = os.getenv("TELEGRAM_TOKEN", "8510876943:AAGO4QjhMWbJL_Z630RbHjyTbhaK0qHI1N0")
SHEET_ID = os.getenv("SHEET_ID", "14iTFjqHSKFPdLT9rieop6lFozA9ZkC_zYmfjjjV7HlU")
CREDS_FILE = os.getenv("GOOGLE_CREDS_PATH", r"G:\Meu Drive\Antigravity\Bitcoin\certs\google_creds.json")

# Se estivermos rodando no Linux (Dell Node ou Cloud), ajustamos o caminho das credenciais
if not os.path.exists(CREDS_FILE) and os.path.exists("google_creds.json"):
    CREDS_FILE = "google_creds.json"

# Usuários autorizados (Lista no .env facilitada por vírgulas)
auth_str = os.getenv("AUTHORIZED_USERS", "639141171,6099953061")
AUTHORIZED_USERS = [int(uid.strip()) for uid in auth_str.split(',') if uid.strip().isdigit()]

PENDING_FILE = "pending_gastos.json"

def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # Tenta ler como arquivo, se falhar ou não existir, tenta ler direto do JSON se passarmos via env (opcional)
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
    except Exception as e:
        logger.error(f"Erro ao carregar credenciais: {e}")
        raise
    return gspread.authorize(creds)

def get_monthly_sheet():
    client = get_gspread_client()
    spreadsheet = client.open_by_key(SHEET_ID)
    
    # Nome da aba: "MM-YYYY"
    month_name = datetime.now().strftime("%m-%Y")
    
    try:
        sheet = spreadsheet.worksheet(month_name)
    except gspread.exceptions.WorksheetNotFound:
        # Criar a aba se não existir
        sheet = spreadsheet.add_worksheet(title=month_name, rows="1000", cols="8")
        headers = ["Dia", "Hora", "Usuário", "Descrição", "Categoria", "Prioridade", "Pagamento", "Valor"]
        sheet.append_row(headers)
    
    return sheet

def is_authorized(user_id):
    logger.info(f"Checando autorização para o ID: {user_id}")
    if not AUTHORIZED_USERS:
        return True
    return user_id in AUTHORIZED_USERS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "usuário"
    logger.info(f"Comando /start recebido de {user_name} (ID: {user_id})")
    
    if not is_authorized(user_id):
        await update.message.reply_text(f"⛔ Acesso não autorizado. Seu ID é: {user_id}")
        return

    message = (
        f"<b>Olá {user_name}! Eu sou o seu Bot de Controle Financeiro (Modo 24h).</b> 🚀\n\n"
        "Sempre que precisar anotar um gasto, envie no formato:\n"
        "<code>Descrição / Categoria / Lazer ou Essencial / Forma de Pagamento / Valor</code>\n\n"
        "<b>Exemplo:</b>\n"
        "<code>Almoço / Alimentação / Essencial / Pix / 35.50</code>\n\n"
        "<b>Dashboard Online:</b>\n"
        f"<a href='https://dashboard-profit.streamlit.app'>Abrir Gráficos de Gastos</a>\n"
    )
    await update.message.reply_html(message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text(f"⛔ Acesso não autorizado. Seu ID: {user_id}")
        return

    text = update.message.text
    user = update.effective_user.first_name or "usuário"
    logger.info(f"Mensagem recebida de {user}: {text}")
    
    parts = [p.strip() for p in text.split('/')]
    
    if len(parts) == 5:
        try:
            descricao, categoria, prioridade, pagamento, valor_str = parts
            clean_valor = valor_str.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
            valor = float(clean_valor)
            
            now = datetime.now()
            dia = now.strftime("%d/%m/%Y")
            hora = now.strftime("%H:%M:%S")
            month_ref = now.strftime("%m-%Y")
            
            # Conexão com Sheets
            client = get_gspread_client()
            spreadsheet = client.open_by_key(SHEET_ID)
            
            # 1. Carregar aba mensal e checar duplicatas
            sheet_mensal = get_monthly_sheet()
            records = sheet_mensal.get_all_values()
            
            # Checar se já existe: [Dia, Hora, User, Descrição, Categoria, Prioridade, Pagamento, Valor]
            # Critério de duplicata: Mesmo Dia, Usuário, Descrição e Valor (Ignorando Hora exata)
            # Valor na planilha vem como string com vírgula ou ponto dependendo da localidade, mas aqui vamos comparar o valor numérico
            is_dup = False
            for r in records[1:]: # Ignora o cabeçalho
                if len(r) >= 8:
                    try:
                        r_dia, _, r_user, r_desc, r_cat, _, _, r_val_str = r[0:8]
                        # Limpeza básica do valor da planilha para comparação
                        r_val = float(str(r_val_str).replace('R$', '').replace('.', '').replace(',', '.'))
                        if r_dia == dia and r_user == user and r_desc.lower() == descricao.lower() and abs(r_val - valor) < 0.01:
                            is_dup = True
                            break
                    except: continue

            if is_dup:
                logger.warning(f"Duplicata detectada para {user}: {descricao} de R$ {valor}")
                await update.message.reply_text(f"⚠️ **Atenção:** Este gasto já foi registrado hoje!\n📝 {descricao}: R$ {valor:.2f}\n(Lançamento duplicado ignorado)")
                return

            # 2. Salvar na aba mensal
            row = [dia, hora, user, descricao, categoria, prioridade, pagamento, valor]
            sheet_mensal.append_row(row)
            
            # 3. Salvar na aba Consolidado
            try:
                sheet_consolidado = spreadsheet.worksheet("Consolidado")
            except gspread.exceptions.WorksheetNotFound:
                sheet_consolidado = spreadsheet.add_worksheet(title="Consolidado", rows="1000", cols="9")
                headers = ["Dia", "Hora", "Usuário", "Descrição", "Categoria", "Prioridade", "Pagamento", "Valor", "Mês_Ref"]
                sheet_consolidado.append_row(headers)
            sheet_consolidado.append_row(row + [month_ref])

            # Enviar confirmação imediata
            link_sheet = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"
            response = (
                f"✅ <b>Gasto anotado!</b>\n"
                f"📝 {descricao}: R$ {valor:.2f}\n"
                f"📍 {dia} às {hora}\n\n"
                f"🔗 <a href='{link_sheet}'>Ver Planilha</a>"
            )
            await update.message.reply_html(response)
            
        except ValueError as e:
            logger.error(f"Erro de valor: {valor_str} -> {e}")
            await update.message.reply_text("❌ Erro no valor. Use o formato por ex: 35.50 ou 35,50")
        except Exception as e:
            logger.error(f"Erro ao processar mensagem (salvando para retry): {e}")
            # Salvar para processamento posterior
            pending_item = {
                "chat_id": update.effective_chat.id,
                "user": user,
                "data": {
                    "descricao": descricao,
                    "categoria": categoria,
                    "prioridade": prioridade,
                    "pagamento": pagamento,
                    "valor": valor,
                    "dia": dia,
                    "hora": hora,
                    "month_ref": month_ref
                }
            }
            save_pending(pending_item)
            await update.message.reply_text(f"⏳ **Offline:** Salvei seu gasto localmente devido a uma falha de conexão. Ele será sincronizado automaticamente quando a internet/planilha voltar!")

def save_pending(item):
    try:
        pending = []
        if os.path.exists(PENDING_FILE):
            with open(PENDING_FILE, "r", encoding="utf-8") as f:
                pending = json.load(f)
        pending.append(item)
        with open(PENDING_FILE, "w", encoding="utf-8") as f:
            json.dump(pending, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Erro ao salvar pendente: {e}")

async def process_pending_job(context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(PENDING_FILE):
        return
    
    try:
        with open(PENDING_FILE, "r", encoding="utf-8") as f:
            pending = json.load(f)
    except: return

    if not pending:
        return

    logger.info(f"🔄 Tentando sincronizar {len(pending)} gastos pendentes...")
    still_pending = []
    synchronized_count = 0

    try:
        client = get_gspread_client()
        spreadsheet = client.open_by_key(SHEET_ID)
        
        for item in pending:
            try:
                chat_id = item["chat_id"]
                d = item["data"]
                
                # 1. Mensal
                # Nota: para simplificar, assume-se que o mês ainda é o mesmo ou que get_monthly_sheet lida com isso
                # Mas aqui usamos a data original do registro
                month_name = d["month_ref"]
                try:
                    sheet_mensal = spreadsheet.worksheet(month_name)
                except:
                    sheet_mensal = spreadsheet.add_worksheet(title=month_name, rows="1000", cols="8")
                    headers = ["Dia", "Hora", "Usuário", "Descrição", "Categoria", "Prioridade", "Pagamento", "Valor"]
                    sheet_mensal.append_row(headers)
                
                row = [d["dia"], d["hora"], item["user"], d["descricao"], d["categoria"], d["prioridade"], d["pagamento"], d["valor"]]
                sheet_mensal.append_row(row)
                
                # 2. Consolidado
                try:
                    sheet_consolidado = spreadsheet.worksheet("Consolidado")
                except:
                    sheet_consolidado = spreadsheet.add_worksheet(title="Consolidado", rows="1000", cols="9")
                    headers = ["Dia", "Hora", "Usuário", "Descrição", "Categoria", "Prioridade", "Pagamento", "Valor", "Mês_Ref"]
                    sheet_consolidado.append_row(headers)
                sheet_consolidado.append_row(row + [d["month_ref"]])

                # 3. Notificar usuário
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"✅ **Sincronizado!**\nO gasto de R$ {d['valor']:.2f} ({d['descricao']}) foi inserido na planilha com sucesso agora que a conexão voltou.",
                    parse_mode='HTML'
                )
                synchronized_count += 1
            except Exception as e:
                logger.error(f"Falha ao re-sincronizar item: {e}")
                still_pending.append(item)
    except Exception as e:
        logger.error(f"Erro geral no job de sincronização: {e}")
        still_pending = pending

    # Atualizar arquivo
    try:
        with open(PENDING_FILE, "w", encoding="utf-8") as f:
            json.dump(still_pending, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Erro ao atualizar pendentes: {e}")

    if synchronized_count > 0:
        logger.info(f"✅ Sincronização concluída: {synchronized_count} itens processados.")
    else:
        await start(update, context)

async def get_df_monthly():
    sheet = get_monthly_sheet()
    data = sheet.get_all_records()
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)

async def category_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id): return
    try:
        df = await get_df_monthly()
        if df.empty:
            await update.message.reply_text("📭 Sem dados no mês atual.")
            return
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
        cat_summary = df.groupby('Categoria')['Valor'].sum().sort_values(ascending=False)
        text = "<b>📂 Gastos por Categoria (Mês Atual):</b>\n" + "\n".join([f"• {cat}: R$ {val:.2f}" for cat, val in cat_summary.items()])
        await update.message.reply_html(text)
    except Exception as e: logger.error(f"Erro categoria: {e}")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id): return
    try:
        df = await get_df_monthly()
        if df.empty:
            await update.message.reply_text("📭 Nenhuma despesa anotada neste mês.")
            return
        total = pd.to_numeric(df['Valor'], errors='coerce').sum()
        count = len(df)
        message = (
            f"<b>📊 Resumo Mensal ({datetime.now().strftime('%m/%Y')})</b>\n\n"
            f"💰 Total Gasto: R$ {total:.2f}\n"
            f"🔢 Itens: {count}"
        )
        await update.message.reply_html(message)
    except Exception as e: logger.error(f"Erro nas stats: {e}")

if __name__ == '__main__':
    logger.info("Iniciando o bot de gastos (Hospedagem 24h)...")
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Configurar JobQueue para sincronização offline
    job_queue = application.job_queue
    job_queue.run_repeating(process_pending_job, interval=300, first=10) # A cada 5 minutos
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('stats', stats))
    application.add_handler(CommandHandler('categoria', category_summary))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot rodando com sucesso.")
    application.run_polling()
