"""
Telegram Personal Assistant Bot
Features: Tabungan, Pengeluaran, Notes

Deploy to Hugging Face Spaces for 24/7 operation
"""

import os
import logging
import asyncio
import threading
from flask import Flask
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

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = os.environ.get("OWNER_ID")

# Flask app for Hugging Face health check
flask_app = Flask(__name__)


@flask_app.route("/")
def home():
    return "Bot is running!"


@flask_app.route("/health")
def health():
    return "OK"


def run_flask():
    """Run Flask in background thread"""
    port = int(os.environ.get("PORT", 7860))
    flask_app.run(host="0.0.0.0", port=port, use_reloader=False)


def is_owner(user_id: int) -> bool:
    """Check if user is the owner"""
    if not OWNER_ID:
        return True
    return str(user_id) == str(OWNER_ID)


async def owner_only(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check owner permission"""
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("Akses ditolak. Bot ini hanya untuk pemilik.")
        return False
    return True


# ==================== COMMAND HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
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
    """Handle /help command"""
    if not await owner_only(update, context):
        return
    
    await update.message.reply_text(
        "TABUNGAN\n"
        "/tabung 50000 - nabung\n"
        "/ambil 25000 - ambil\n"
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


# ==================== WRAPPER HANDLERS ====================

async def tabung_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update, context):
        return
    await handle_tabung(update, context)


async def ambil_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update, context):
        return
    await handle_ambil(update, context)


async def saldo_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update, context):
        return
    await handle_saldo(update, context)


async def keluar_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update, context):
        return
    await handle_keluar(update, context)


async def laporan_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update, context):
        return
    await handle_laporan(update, context)


async def laporan_bulan_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update, context):
        return
    await handle_laporan_bulan(update, context)


async def note_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update, context):
        return
    await handle_note(update, context)


async def notes_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update, context):
        return
    await handle_notes(update, context)


async def lihat_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update, context):
        return
    await handle_lihat(update, context)


async def hapus_note_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update, context):
        return
    await handle_hapus_note(update, context)


async def edit_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update, context):
        return
    await handle_edit(update, context)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands"""
    if not await owner_only(update, context):
        return
    await update.message.reply_text(
        "Command tidak dikenal. Ketik /help untuk melihat daftar command."
    )


async def post_init(application: Application):
    """Set bot commands after initialization"""
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


def main():
    """Start the bot"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set!")
        # Still run Flask for health check
        run_flask()
        return
    
    # Initialize database
    db.init_database()
    logger.info("Database initialized")
    
    # Start Flask in background thread for health check
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("Flask server started on port 7860")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Savings handlers
    application.add_handler(CommandHandler("tabung", tabung_wrapper))
    application.add_handler(CommandHandler("ambil", ambil_wrapper))
    application.add_handler(CommandHandler("saldo", saldo_wrapper))
    
    # Expenses handlers
    application.add_handler(CommandHandler("keluar", keluar_wrapper))
    application.add_handler(CommandHandler("laporan", laporan_wrapper))
    application.add_handler(CommandHandler("laporan_bulan", laporan_bulan_wrapper))
    
    # Notes handlers
    application.add_handler(CommandHandler("note", note_wrapper))
    application.add_handler(CommandHandler("edit", edit_wrapper))
    application.add_handler(CommandHandler("notes", notes_wrapper))
    application.add_handler(CommandHandler("lihat", lihat_wrapper))
    application.add_handler(CommandHandler("hapus_note", hapus_note_wrapper))
    
    # Unknown command handler
    application.add_handler(MessageHandler(filters.COMMAND, unknown))
    
    # Start polling in main thread
    logger.info("Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
