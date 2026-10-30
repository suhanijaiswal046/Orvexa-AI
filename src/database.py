"""SQLite persistence for support tickets."""
import sqlite3
from datetime import datetime, timezone
from src.config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                issue TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Open',
                created_at TEXT NOT NULL
            )
        """)

def create_ticket(name: str, issue: str, priority: str) -> int:
    init_db()
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO tickets(name, issue, priority, created_at) VALUES (?, ?, ?, ?)",
            (name, issue, priority, datetime.now(timezone.utc).isoformat())
        )
        return int(cur.lastrowid)

def list_tickets(limit: int = 100):
    init_db()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM tickets ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(row) for row in rows]
