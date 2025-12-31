"""
Expenses tracking feature handlers
"""

from datetime import datetime, timedelta
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


async def handle_keluar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /keluar command - record an expense"""
    if len(context.args) < 2:
        await update.message.reply_text(
            "Cara penggunaan: /keluar <jumlah> <keterangan>\n"
            "Contoh: /keluar 10k jajan\n"
            "Contoh: /keluar 50000 makan siang\n\n"
            "Tips: Bisa pakai 'k' atau 'rb' untuk ribuan, 'jt' untuk jutaan"
        )
        return
    
    try:
        amount = parse_amount(context.args[0])
        description = " ".join(context.args[1:])
        
        if amount <= 0:
            await update.message.reply_text("Jumlah harus lebih dari 0")
            return
        
        db.add_expense(amount, description)
        
        await update.message.reply_text(
            f"Pengeluaran tercatat:\n"
            f"  Jumlah: Rp {amount:,.0f}\n"
            f"  Keterangan: {description}\n"
            f"  Waktu: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )
        
    except ValueError:
        await update.message.reply_text("Jumlah tidak valid. Contoh: 10k, 50000, 1jt")


async def handle_laporan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /laporan command - weekly expense report"""
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_week = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    expenses = db.get_expenses_by_period(start_of_week, end_of_week)
    total = db.get_total_expenses_by_period(start_of_week, end_of_week)
    
    if not expenses:
        await update.message.reply_text("Tidak ada pengeluaran minggu ini.")
        return
    
    message = "LAPORAN PENGELUARAN MINGGU INI\n"
    message += f"Periode: {start_of_week.strftime('%d/%m/%Y')} - {today.strftime('%d/%m/%Y')}\n"
    message += "=" * 35 + "\n\n"
    
    # Group by date
    expenses_by_date = {}
    for exp in expenses:
        date_str = exp["created_at"][:10]
        if date_str not in expenses_by_date:
            expenses_by_date[date_str] = []
        expenses_by_date[date_str].append(exp)
    
    for date_str, date_expenses in sorted(expenses_by_date.items(), reverse=True):
        date_obj = datetime.fromisoformat(date_str)
        message += f"[{date_obj.strftime('%d/%m/%Y')}]\n"
        
        for exp in date_expenses:
            time_str = exp["created_at"][11:16]
            message += f"  {time_str} - {exp['description']}: Rp {exp['amount']:,.0f}\n"
        
        message += "\n"
    
    message += "=" * 35 + "\n"
    message += f"TOTAL: Rp {total:,.0f}"
    
    await update.message.reply_text(message)


async def handle_laporan_bulan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /laporan_bulan command - monthly expense report"""
    today = datetime.now()
    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_month = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    expenses = db.get_expenses_by_period(start_of_month, end_of_month)
    total = db.get_total_expenses_by_period(start_of_month, end_of_month)
    
    if not expenses:
        await update.message.reply_text("Tidak ada pengeluaran bulan ini.")
        return
    
    message = "LAPORAN PENGELUARAN BULAN INI\n"
    message += f"Periode: {start_of_month.strftime('%B %Y')}\n"
    message += "=" * 35 + "\n\n"
    
    # Group by date
    expenses_by_date = {}
    for exp in expenses:
        date_str = exp["created_at"][:10]
        if date_str not in expenses_by_date:
            expenses_by_date[date_str] = []
        expenses_by_date[date_str].append(exp)
    
    for date_str, date_expenses in sorted(expenses_by_date.items(), reverse=True):
        date_obj = datetime.fromisoformat(date_str)
        daily_total = sum(e["amount"] for e in date_expenses)
        message += f"[{date_obj.strftime('%d/%m/%Y')}] - Total: Rp {daily_total:,.0f}\n"
        
        for exp in date_expenses:
            time_str = exp["created_at"][11:16]
            message += f"    {time_str} - {exp['description']}: Rp {exp['amount']:,.0f}\n"
        
        message += "\n"
    
    message += "=" * 35 + "\n"
    message += f"TOTAL BULAN INI: Rp {total:,.0f}"
    
    await update.message.reply_text(message)
