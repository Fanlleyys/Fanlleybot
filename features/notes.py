"""
Notes feature handlers - for storing passwords and notes
"""

from telegram import Update
from telegram.ext import ContextTypes
import database as db


async def handle_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /note command - save a note"""
    if len(context.args) < 2:
        await update.message.reply_text(
            "Cara penggunaan: /note <judul> <isi>\n"
            "Contoh: /note gmail password123\n"
            "Contoh: /note wifi rumah MyWifiPassword123"
        )
        return
    
    title = context.args[0].lower()
    content = " ".join(context.args[1:])
    
    success, message = db.save_note(title, content)
    await update.message.reply_text(message)


async def handle_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /notes command - list all notes"""
    notes = db.get_all_notes()
    
    if not notes:
        await update.message.reply_text(
            "Belum ada catatan tersimpan.\n"
            "Gunakan /note <judul> <isi> untuk menyimpan."
        )
        return
    
    message = "DAFTAR CATATAN\n"
    message += "=" * 30 + "\n\n"
    
    for note in notes:
        updated = note["updated_at"][:10]
        message += f"- {note['title']} (update: {updated})\n"
    
    message += "\n" + "=" * 30 + "\n"
    message += "Ketik /lihat <judul> untuk melihat isi"
    
    await update.message.reply_text(message)


async def handle_lihat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /lihat command - view a specific note"""
    if not context.args:
        await update.message.reply_text(
            "Cara penggunaan: /lihat <judul>\n"
            "Contoh: /lihat gmail"
        )
        return
    
    title = context.args[0].lower()
    note = db.get_note_by_title(title)
    
    if not note:
        await update.message.reply_text(f"Catatan '{title}' tidak ditemukan.")
        return
    
    message = f"CATATAN: {note['title'].upper()}\n"
    message += "=" * 30 + "\n\n"
    message += f"{note['content']}\n\n"
    message += "=" * 30 + "\n"
    message += f"Dibuat: {note['created_at'][:10]}\n"
    message += f"Update: {note['updated_at'][:10]}"
    
    await update.message.reply_text(message)


async def handle_hapus_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /hapus_note command - delete a note"""
    if not context.args:
        await update.message.reply_text(
            "Cara penggunaan: /hapus_note <judul>\n"
            "Contoh: /hapus_note gmail"
        )
        return
    
    title = context.args[0].lower()
    success, message = db.delete_note(title)
    await update.message.reply_text(message)
