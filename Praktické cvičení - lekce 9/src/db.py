import sqlite3
from pathlib import Path

DB_PATH = Path("agent.db")

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        con.commit()

def save_note(title: str, content: str) -> int:
    with sqlite3.connect(DB_PATH) as con:
        cur = con.execute(
            "INSERT INTO notes(title, content) VALUES(?, ?)",
            (title, content)
        )
        con.commit()
        return cur.lastrowid

def search_notes(query: str, limit: int = 5) -> list[dict]:
    q = f"%{query}%"
    with sqlite3.connect(DB_PATH) as con:
        cur = con.execute(
            "SELECT id, title, content, created_at FROM notes "
            "WHERE title LIKE ? OR content LIKE ? "
            "ORDER BY created_at DESC LIMIT ?",
            (q, q, limit)
        )
        rows = cur.fetchall()
    return [{"id": r[0], "title": r[1], "content": r[2], "created_at": r[3]} for r in rows]
