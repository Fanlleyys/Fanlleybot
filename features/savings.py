"""
Savings feature handlers
"""

from telegram import Update
from telegram.ext import ContextTypes
import database as db


async def handle_tabung(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /tabung command - add to savings"""
    if not context.args:
        await update.message.reply_text(
            "Cara penggunaan: /tabung <jumlah>\n"
            "Contoh: /tabung 50000"
        )
        return
    
    try:
        amount = float(context.args[0].replace(",", "").replace(".", ""))
        
        if amount <= 0:
            await update.message.reply_text("Jumlah harus lebih dari 0")
            return
        
        new_balance = db.add_savings(amount)
        
        await update.message.reply_text(
            f"Berhasil menabung Rp {amount:,.0f}\n"
            f"Saldo tabungan sekarang: Rp {new_balance:,.0f}"
        )
        
    except ValueError:
        await update.message.reply_text("Jumlah tidak valid. Gunakan angka saja.")


async def handle_ambil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ambil command - withdraw from savings"""
    if not context.args:
        await update.message.reply_text(
            "Cara penggunaan: /ambil <jumlah>\n"
            "Contoh: /ambil 25000"
        )
        return
    
    try:
        amount = float(context.args[0].replace(",", "").replace(".", ""))
        
        if amount <= 0:
            await update.message.reply_text("Jumlah harus lebih dari 0")
            return
        
        success, balance, message = db.withdraw_savings(amount)
        await update.message.reply_text(message)
        
    except ValueError:
        await update.message.reply_text("Jumlah tidak valid. Gunakan angka saja.")


async def handle_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /saldo command - check savings balance"""
    balance = db.get_savings_balance()
    
    # Get recent history
    history = db.get_savings_history(5)
    
    message = f"Saldo tabungan: Rp {balance:,.0f}\n\n"
    
    if history:
        message += "Transaksi terakhir:\n"
        for tx in history:
            tx_type = "+" if tx["transaction_type"] == "deposit" else "-"
            tx_amount = abs(tx["amount"])
            tx_date = tx["created_at"][:10]
            message += f"  {tx_date} | {tx_type}Rp {tx_amount:,.0f}\n"
    
    await update.message.reply_text(message)
