import logging
import pandas as pd
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import os

# Configuração de logs para ver o que está acontecendo
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

import gspread
from oauth2client.service_account import ServiceAccountCredentials

TOKEN = "8510876943:AAGO4QjhMWbJL_Z630RbHjyTbhaK0qHI1N0"
SHEET_ID = "14iTFjqHSKFPdLT9rieop6lFozA9ZkC_zYmfjjjV7HlU"
CREDS_FILE = r"G:\Meu Drive\Antigravity\Bitcoin\certs\google_creds.json"

# Usuários autorizados
AUTHORIZED_USERS = [639141171, 6099953061]

def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
    return gspread.authorize(creds)

def get_monthly_sheet():
    client = get_gspread_client()
    spreadsheet = client.open_by_key(SHEET_ID)
    
    # Nome da aba: "03-2026"
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
        f"<b>Olá {user_name}! Eu sou o seu Bot de Controle Financeiro.</b> 🚀\n\n"
        "Sempre que precisar anotar um gasto, envie no formato:\n"
        "<code>Descrição / Categoria / Lazer ou Essencial / Forma de Pagamento / Valor</code>\n\n"
        "<b>Exemplo:</b>\n"
        "<code>Almoço / Alimentação / Essencial / Pix / 35.50</code>\n\n"
        "<b>Comandos:</b>\n"
        "/start - Mostra estas instruções\n"
        "/stats - Resumo mensal (aba atual)\n"
        "/categoria - Resumo por categoria\n"
        "/pix - Consolidação Pix\n"
        "/debito - Consolidação Débito\n"
        "/credito - Consolidação Crédito\n"
        "/dashboard - Link direto para os gráficos\n\n"
        "✨ <b>Dashboard Online:</b>\n"
        f"<a href='https://dashboard-profit.streamlit.app'>Abrir Gráficos de Gastos</a>\n"
        "---"
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
            
            # 1. Salvar na aba mensal
            sheet_mensal = get_monthly_sheet()
            row = [dia, hora, user, descricao, categoria, prioridade, pagamento, valor]
            sheet_mensal.append_row(row)
            
            # 2. Salvar na aba Consolidado
            try:
                sheet_consolidado = spreadsheet.worksheet("Consolidado")
            except gspread.exceptions.WorksheetNotFound:
                sheet_consolidado = spreadsheet.add_worksheet(title="Consolidado", rows="1000", cols="9")
                headers = ["Dia", "Hora", "Usuário", "Descrição", "Categoria", "Prioridade", "Pagamento", "Valor", "Mês_Ref"]
                sheet_consolidado.append_row(headers)
            sheet_consolidado.append_row(row + [month_ref])

            # 3. CÁLCULO DE SALDO (REAL-TIME)
            saldo_info = ""
            try:
                plan_sheet = spreadsheet.worksheet("Planejamento")
                plan_data = plan_sheet.get_all_records()
                meta = next((float(str(item['Gasto Máximo Mensal']).replace(',', '.')) for item in plan_data if item['Categoria'].lower() == categoria.lower()), 0.0)
                
                if meta > 0:
                    records = sheet_mensal.get_all_records()
                    total_cat = sum(float(str(r['Valor']).replace(',', '.')) for r in records if str(r['Categoria']).lower() == categoria.lower())
                    restante = meta - total_cat
                    saldo_info = f"\n\n💰 <b>Saldo em {categoria}:</b>\nMeta: R$ {meta:.2f}\nRestante: R$ {restante:.2f}"
                    if restante < 0:
                        saldo_info += " ⚠️ (Limite Excedido!)"
            except Exception as e:
                logger.error(f"Erro saldo: {e}")

            link_sheet = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"
            response = (
                f"✅ <b>Gasto anotado!</b>\n"
                f"📝 {descricao}: R$ {valor:.2f}\n"
                f"📍 {dia} às {hora}"
                f"{saldo_info}\n\n"
                f"🔗 <a href='{link_sheet}'>Ver Planilha</a>"
            )
            await update.message.reply_html(response)
            
        except ValueError as e:
            logger.error(f"Erro de valor: {valor_str} -> {e}")
            await update.message.reply_text("❌ Erro no valor. Use o formato por ex: 35.50 ou 35,50")
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            await update.message.reply_text(f"❌ Erro operacional: {str(e)}")
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
        # Converter Valor para numérico por segurança
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
        cat_summary = df.groupby('Categoria')['Valor'].sum().sort_values(ascending=False)
        text = "<b>📂 Gastos por Categoria (Mês Atual):</b>\n" + "\n".join([f"• {cat}: R$ {val:.2f}" for cat, val in cat_summary.items()])
        await update.message.reply_html(text)
    except Exception as e: logger.error(f"Erro categoria: {e}")

async def payment_summary(update: Update, context: ContextTypes.DEFAULT_TYPE, method: str):
    user_id = update.effective_user.id
    if not is_authorized(user_id): return
    try:
        df = await get_df_monthly()
        if df.empty:
            await update.message.reply_text("📭 Sem dados.")
            return
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
        df_filtered = df[df['Pagamento'].str.contains(method, case=False, na=False)]
        
        if df_filtered.empty:
            await update.message.reply_text(f"📭 Nenhum gasto com {method} encontrado.")
            return
            
        total = df_filtered['Valor'].sum()
        count = len(df_filtered)
        latest = df_filtered.tail(5)
        latest_text = "\n".join([f"• {row['Descrição']}: R$ {row['Valor']:.2f}" for _, row in latest.iterrows()])
        
        message = (
            f"<b>💳 Consolidação {method.upper()}</b>\n\n"
            f"💰 Total: R$ {total:.2f}\n"
            f"🔢 Quantidade: {count}\n\n"
            f"<b>Últimos lançamentos:</b>\n{latest_text}"
        )
        await update.message.reply_html(message)
    except Exception as e: logger.error(f"Erro pagamento {method}: {e}")

async def pix_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await payment_summary(update, context, "Pix")

async def debito_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await payment_summary(update, context, "Débito")

async def credito_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await payment_summary(update, context, "Crédito")

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
        cat_summary = df.groupby('Categoria')['Valor'].sum().to_dict()
        cat_text = "\n".join([f"• {cat}: R$ {val:.2f}" for cat, val in cat_summary.items()])
        
        message = (
            f"<b>📊 Resumo Mensal ({datetime.now().strftime('%m/%Y')})</b>\n\n"
            f"💰 Total Gasto: R$ {total:.2f}\n"
            f"🔢 Itens: {count}\n\n"
            f"🗂 <b>Por Categoria:</b>\n{cat_text}"
        )
        await update.message.reply_html(message)
    except Exception as e:
        logger.error(f"Erro nas stats: {e}")

async def dashboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id): return
    
    message = (
        "<b>📊 Dashboard Exclusivo de Despesas</b>\n\n"
        "Estou preparando o novo link privado para você! 🚀\n"
        "<i>Use o arquivo ABRIR_DASHBOARD_GASTOS.bat enquanto o link online não fica pronto.</i>"
    )
    await update.message.reply_html(message)

if __name__ == '__main__':
    logger.info("Iniciando o bot com Google Sheets...")
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('stats', stats))
    application.add_handler(CommandHandler('categoria', category_summary))
    application.add_handler(CommandHandler('pix', pix_command))
    application.add_handler(CommandHandler('debito', debito_command))
    application.add_handler(CommandHandler('credito', credito_command))
    application.add_handler(CommandHandler('dashboard', dashboard_command))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot rodando com sucesso (Google Sheets).")
    application.run_polling()
