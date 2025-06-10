import sqlite3
import os
from datetime import datetime
import uuid

DB_PATH = "data/robots.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Robot table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS robots (
        id TEXT PRIMARY KEY, -- UUID as TEXT
        created_at TEXT NOT NULL,
        nom TEXT
    )
    """)
    # Mission table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS missions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        robot_id TEXT NOT NULL,
        cube INTEGER NOT NULL,
        etat TEXT NOT NULL CHECK(etat IN ('en_cours', 'terminé', 'à_faire')),
        FOREIGN KEY(robot_id) REFERENCES robots(id)
    )
    """)
    # StatutRobot table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS statut_robot (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        robot_id TEXT NOT NULL,
        position TEXT NOT NULL,
        horodatage TEXT NOT NULL,
        etat TEXT NOT NULL,
        FOREIGN KEY(robot_id) REFERENCES robots(id)
    )
    """)
    conn.commit()
    conn.close()

def insert_robot(nom=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    robot_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()
    cursor.execute("INSERT INTO robots (id, created_at, nom) VALUES (?, ?, ?)",
                   (robot_id, created_at, nom))
    conn.commit()
    conn.close()
    return robot_id

def get_all_robots():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, created_at, nom FROM robots")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": r[0], "created_at": r[1], "nom": r[2]}
        for r in rows
    ]

def insert_mission(robot_id, cube, etat):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO missions (robot_id, cube, etat) VALUES (?, ?, ?)",
                   (robot_id, cube, etat))
    conn.commit()
    conn.close()

def get_all_missions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, robot_id, cube, etat FROM missions")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": r[0], "robot_id": r[1], "cube": r[2], "etat": r[3]}
        for r in rows
    ]

def insert_statut_robot(robot_id, position, horodatage, etat):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO statut_robot (robot_id, position, horodatage, etat) VALUES (?, ?, ?, ?)",
                   (robot_id, position, horodatage, etat))
    conn.commit()
    conn.close()

def get_all_statut_robot():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, robot_id, position, horodatage, etat FROM statut_robot")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": r[0], "robot_id": r[1], "position": r[2], "horodatage": r[3], "etat": r[4]}
        for r in rows
    ]
