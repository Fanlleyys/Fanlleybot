"""
Database module for Telegram Personal Assistant Bot
Uses SQLite for data persistence
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Tuple, Optional

DATABASE_PATH = os.environ.get("DATABASE_PATH", "bot_data.db")


def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Savings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS savings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            transaction_type TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    # Expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            description TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    # Notes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()


# ==================== SAVINGS ====================

def add_savings(amount: float) -> float:
    """Add money to savings, returns new balance"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO savings (amount, transaction_type, created_at) VALUES (?, ?, ?)",
        (amount, "deposit", datetime.now().isoformat())
    )
    
    conn.commit()
    conn.close()
    
    return get_savings_balance()


def withdraw_savings(amount: float) -> Tuple[bool, float, str]:
    """Withdraw from savings, returns (success, balance, message)"""
    current_balance = get_savings_balance()
    
    if amount > current_balance:
        return False, current_balance, f"Saldo tidak cukup. Saldo saat ini: Rp {current_balance:,.0f}"
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO savings (amount, transaction_type, created_at) VALUES (?, ?, ?)",
        (-amount, "withdraw", datetime.now().isoformat())
    )
    
    conn.commit()
    conn.close()
    
    new_balance = get_savings_balance()
    return True, new_balance, f"Berhasil mengambil Rp {amount:,.0f}. Saldo sekarang: Rp {new_balance:,.0f}"


def get_savings_balance() -> float:
    """Get current savings balance"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COALESCE(SUM(amount), 0) as balance FROM savings")
    result = cursor.fetchone()
    
    conn.close()
    
    return result["balance"] if result else 0


def get_savings_history(limit: int = 10) -> List[dict]:
    """Get savings transaction history"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM savings ORDER BY created_at DESC LIMIT ?",
        (limit,)
    )
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


# ==================== EXPENSES ====================

def add_expense(amount: float, description: str) -> int:
    """Add an expense record, returns expense id"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO expenses (amount, description, created_at) VALUES (?, ?, ?)",
        (amount, description, datetime.now().isoformat())
    )
    
    expense_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return expense_id


def get_expenses_by_period(start_date: datetime, end_date: datetime) -> List[dict]:
    """Get expenses within a date range"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT * FROM expenses 
        WHERE created_at >= ? AND created_at <= ?
        ORDER BY created_at DESC
        """,
        (start_date.isoformat(), end_date.isoformat())
    )
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_total_expenses_by_period(start_date: datetime, end_date: datetime) -> float:
    """Get total expenses within a date range"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT COALESCE(SUM(amount), 0) as total FROM expenses 
        WHERE created_at >= ? AND created_at <= ?
        """,
        (start_date.isoformat(), end_date.isoformat())
    )
    
    result = cursor.fetchone()
    conn.close()
    
    return result["total"] if result else 0


# ==================== NOTES ====================

def save_note(title: str, content: str) -> Tuple[bool, str]:
    """Save or update a note"""
    conn = get_connection()
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    # Check if note exists
    cursor.execute("SELECT id FROM notes WHERE title = ?", (title,))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute(
            "UPDATE notes SET content = ?, updated_at = ? WHERE title = ?",
            (content, now, title)
        )
        message = f"Catatan '{title}' berhasil diperbarui"
    else:
        cursor.execute(
            "INSERT INTO notes (title, content, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (title, content, now, now)
        )
        message = f"Catatan '{title}' berhasil disimpan"
    
    conn.commit()
    conn.close()
    
    return True, message


def get_all_notes() -> List[dict]:
    """Get all notes (title only)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, title, created_at, updated_at FROM notes ORDER BY updated_at DESC")
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_note_by_title(title: str) -> Optional[dict]:
    """Get a specific note by title"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM notes WHERE title = ?", (title,))
    
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def delete_note(title: str) -> Tuple[bool, str]:
    """Delete a note by title"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM notes WHERE title = ?", (title,))
    existing = cursor.fetchone()
    
    if not existing:
        conn.close()
        return False, f"Catatan '{title}' tidak ditemukan"
    
    cursor.execute("DELETE FROM notes WHERE title = ?", (title,))
    
    conn.commit()
    conn.close()
    
    return True, f"Catatan '{title}' berhasil dihapus"
