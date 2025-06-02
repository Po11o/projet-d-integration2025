import sqlite3
import os
from datetime import datetime

DB_PATH = "data/robots.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS robots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        model TEXT NOT NULL,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def insert_robot(name, model):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO robots (name, model, created_at) VALUES (?, ?, ?)",
                   (name, model, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_all_robots():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, model, created_at FROM robots")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": r[0], "name": r[1], "model": r[2], "created_at": r[3]}
        for r in rows
    ]
