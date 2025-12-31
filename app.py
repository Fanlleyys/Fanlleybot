"""
Telegram Personal Assistant Bot - Webhook Version
For HuggingFace Spaces deployment
"""

import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import database as db
from savings import handle_tabung, handle_ambil, handle_saldo
from expenses import handle_keluar, handle_laporan, handle_laporan_bulan
from notes import handle_note, handle_notes, handle_lihat, handle_hapus_note, handle_edit

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = os.environ.get("OWNER_ID")
SPACE_HOST = os.environ.get("SPACE_HOST", "")

# Flask app
app = Flask(__name__)

# Telegram application (global)
application = None


def is_owner(user_id: int) -> bool:
    if not OWNER_ID:
        return True
    return str(user_id) == str(OWNER_ID)


async def owner_only(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("Akses ditolak.")
        return False
    return True


# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update, context):
        return
    user = update.effective_user
    await update.message.reply_text(
        f"Halo {user.first_name}!\n\n"
        "Aku asisten pribadi kamu untuk:\n"
        "- Menabung\n"
        "- Catat pengeluaran\n"
        "- Simpan catatan/password\n\n"
        "Ketik /help untuk lihat cara pakai."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update, context):
        return
    await update.message.reply_text(
        "TABUNGAN\n"
        "/tabung 50k - nabung\n"
        "/ambil 25k - ambil\n"
        "/saldo - cek saldo\n\n"
        "PENGELUARAN\n"
        "/keluar 10k jajan - catat\n"
        "/laporan - minggu ini\n"
        "/laporan_bulan - bulan ini\n\n"
        "CATATAN\n"
        "/note gmail pass123 - simpan\n"
        "/edit gmail newpass - ubah\n"
        "/notes - lihat semua\n"
        "/lihat gmail - buka\n"
        "/hapus_note gmail - hapus\n\n"
        "Tips: 10k = 10.000, 1jt = 1.000.000"
    )


# Wrapper handlers
async def tabung_wrapper(update, context):
    if not await owner_only(update, context): return
    await handle_tabung(update, context)

async def ambil_wrapper(update, context):
    if not await owner_only(update, context): return
    await handle_ambil(update, context)

async def saldo_wrapper(update, context):
    if not await owner_only(update, context): return
    await handle_saldo(update, context)

async def keluar_wrapper(update, context):
    if not await owner_only(update, context): return
    await handle_keluar(update, context)

async def laporan_wrapper(update, context):
    if not await owner_only(update, context): return
    await handle_laporan(update, context)

async def laporan_bulan_wrapper(update, context):
    if not await owner_only(update, context): return
    await handle_laporan_bulan(update, context)

async def note_wrapper(update, context):
    if not await owner_only(update, context): return
    await handle_note(update, context)

async def edit_wrapper(update, context):
    if not await owner_only(update, context): return
    await handle_edit(update, context)

async def notes_wrapper(update, context):
    if not await owner_only(update, context): return
    await handle_notes(update, context)

async def lihat_wrapper(update, context):
    if not await owner_only(update, context): return
    await handle_lihat(update, context)

async def hapus_note_wrapper(update, context):
    if not await owner_only(update, context): return
    await handle_hapus_note(update, context)

async def unknown(update, context):
    if not await owner_only(update, context): return
    await update.message.reply_text("Command tidak dikenal. Ketik /help")


# Flask routes
@app.route("/")
def home():
    return "Bot is running!"


@app.route("/health")
def health():
    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming Telegram updates"""
    if application is None:
        return "Bot not initialized", 500
    
    update = Update.de_json(request.get_json(force=True), application.bot)
    
    # Process update asynchronously
    asyncio.run(application.process_update(update))
    
    return "OK"


async def setup_bot():
    """Initialize bot and set webhook"""
    global application
    
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set!")
        return None
    
    # Initialize database
    db.init_database()
    logger.info("Database initialized")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("tabung", tabung_wrapper))
    application.add_handler(CommandHandler("ambil", ambil_wrapper))
    application.add_handler(CommandHandler("saldo", saldo_wrapper))
    application.add_handler(CommandHandler("keluar", keluar_wrapper))
    application.add_handler(CommandHandler("laporan", laporan_wrapper))
    application.add_handler(CommandHandler("laporan_bulan", laporan_bulan_wrapper))
    application.add_handler(CommandHandler("note", note_wrapper))
    application.add_handler(CommandHandler("edit", edit_wrapper))
    application.add_handler(CommandHandler("notes", notes_wrapper))
    application.add_handler(CommandHandler("lihat", lihat_wrapper))
    application.add_handler(CommandHandler("hapus_note", hapus_note_wrapper))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))
    
    # Initialize
    await application.initialize()
    
    # Set commands
    commands = [
        BotCommand("start", "Mulai bot"),
        BotCommand("help", "Bantuan"),
        BotCommand("tabung", "Menabung"),
        BotCommand("ambil", "Ambil tabungan"),
        BotCommand("saldo", "Cek saldo"),
        BotCommand("keluar", "Catat pengeluaran"),
        BotCommand("laporan", "Laporan minggu ini"),
        BotCommand("laporan_bulan", "Laporan bulan ini"),
        BotCommand("note", "Simpan catatan"),
        BotCommand("edit", "Ubah catatan"),
        BotCommand("notes", "Daftar catatan"),
        BotCommand("lihat", "Lihat catatan"),
        BotCommand("hapus_note", "Hapus catatan"),
    ]
    await application.bot.set_my_commands(commands)
    
    # Set webhook
    if SPACE_HOST:
        webhook_url = f"https://{SPACE_HOST}/webhook"
    else:
        # For HuggingFace, construct URL from space name
        space_name = os.environ.get("SPACE_ID", "")
        if space_name:
            webhook_url = f"https://{space_name.replace('/', '-')}.hf.space/webhook"
        else:
            webhook_url = None
    
    if webhook_url:
        await application.bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook set to: {webhook_url}")
    else:
        logger.warning("Could not set webhook - SPACE_HOST or SPACE_ID not found")
    
    return application


if __name__ == "__main__":
    # Setup bot
    asyncio.run(setup_bot())
    
    # Run Flask
    port = int(os.environ.get("PORT", 7860))
    logger.info(f"Starting Flask on port {port}")
    app.run(host="0.0.0.0", port=port)
