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
            "Contoh: /note gmail password123"
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
        await update.message.reply_text("Belum ada catatan.")
        return
    
    message = "CATATAN\n"
    for note in notes:
        message += f"- {note['title']}\n"
    
    message += "\nKetik /lihat [judul] untuk buka"
    
    await update.message.reply_text(message)


async def handle_lihat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /lihat command - view a specific note"""
    if not context.args:
        await update.message.reply_text("Contoh: /lihat gmail")
        return
    
    title = context.args[0].lower()
    note = db.get_note_by_title(title)
    
    if not note:
        await update.message.reply_text(f"'{title}' tidak ditemukan.")
        return
    
    message = f"{note['title'].upper()}\n"
    message += f"{note['content']}\n\n"
    message += f"Update: {note['updated_at'][:10]}"
    
    await update.message.reply_text(message)


async def handle_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /edit command - edit existing note"""
    if len(context.args) < 2:
        await update.message.reply_text(
            "Contoh: /edit gmail newpassword123"
        )
        return
    
    title = context.args[0].lower()
    
    # Check if note exists
    existing = db.get_note_by_title(title)
    if not existing:
        await update.message.reply_text(
            f"'{title}' tidak ditemukan.\n"
            f"Pakai /note {title} [isi] untuk buat baru."
        )
        return
    
    content = " ".join(context.args[1:])
    success, message = db.save_note(title, content)
    await update.message.reply_text(f"'{title}' berhasil diubah.")


async def handle_hapus_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /hapus_note command - delete a note"""
    if not context.args:
        await update.message.reply_text("Contoh: /hapus_note gmail")
        return
    
    title = context.args[0].lower()
    success, message = db.delete_note(title)
    await update.message.reply_text(message)
