"""
Savings feature handlers
"""

from telegram import Update
from telegram.ext import ContextTypes
import database as db


def parse_amount(text: str) -> float:
    """Parse amount from text like '10k', '10rb', '10000'"""
    text = text.lower().strip()
    
    multiplier = 1
    if text.endswith("k") or text.endswith("rb"):
        multiplier = 1000
        text = text.rstrip("krb")
    elif text.endswith("jt"):
        multiplier = 1000000
        text = text.rstrip("jt")
    
    # Remove any remaining non-numeric except decimal
    text = text.replace(",", "").replace(".", "")
    
    return float(text) * multiplier


async def handle_tabung(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /tabung command - add to savings"""
    if not context.args:
        await update.message.reply_text(
            "Contoh: /tabung 50000 atau /tabung 50k"
        )
        return
    
    try:
        amount = parse_amount(context.args[0])
        
        if amount <= 0:
            await update.message.reply_text("Jumlah harus lebih dari 0")
            return
        
        new_balance = db.add_savings(amount)
        
        await update.message.reply_text(
            f"Nabung Rp {amount:,.0f}\n"
            f"Saldo: Rp {new_balance:,.0f}"
        )
        
    except ValueError:
        await update.message.reply_text("Format salah. Contoh: 50000 atau 50k")


async def handle_ambil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ambil command - withdraw from savings"""
    if not context.args:
        await update.message.reply_text(
            "Contoh: /ambil 25000 atau /ambil 25k"
        )
        return
    
    try:
        amount = parse_amount(context.args[0])
        
        if amount <= 0:
            await update.message.reply_text("Jumlah harus lebih dari 0")
            return
        
        success, balance, message = db.withdraw_savings(amount)
        await update.message.reply_text(message)
        
    except ValueError:
        await update.message.reply_text("Format salah. Contoh: 25000 atau 25k")


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
