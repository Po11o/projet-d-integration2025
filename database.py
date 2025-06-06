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
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        robot_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY(robot_id) REFERENCES robots(id)
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
def insert_movement(robot_id, action):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO movements (robot_id, action, timestamp) VALUES (?, ?, ?)",
                   (robot_id, action, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_all_movements():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.id, r.name, m.action, m.timestamp
        FROM movements m
        JOIN robots r ON m.robot_id = r.id
        ORDER BY m.timestamp DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": r[0], "robot": r[1], "action": r[2], "timestamp": r[3]}
        for r in rows
    ]
