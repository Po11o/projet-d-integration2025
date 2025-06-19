import sqlite3
import os
from datetime import datetime

DB_PATH = "data/robots.db"

# Initialize the database and create necessary tables
def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables if they do not exist
    # This will create the robots, instructions, summary, and telemetry tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS robots (
        id TEXT PRIMARY KEY,
        name TEXT,
        created_at TEXT NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS instructions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        robot_id TEXT NOT NULL,
        blocks TEXT NOT NULL,
        is_completed BOOLEAN DEFAULT FALSE,
        FOREIGN KEY(robot_id) REFERENCES robots(id)
    )
    """)
    
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        robot_id TEXT NOT NULL,
        speed REAL NOT NULL,
        ultrasonic_distance REAL NOT NULL,
        displacement_status TEXT NULL,
        current_line TEXT NOT NULL,
        gripper_state TEXT default 'open',
        time_stamp TEXT default CURRENT_TIMESTAMP,
        FOREIGN KEY(robot_id) REFERENCES robots(id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS summary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        robot_id TEXT NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(robot_id) REFERENCES robots(id)
    )
    """)
    
    conn.commit()
    conn.close()

# insert_robot function to add a new robot to the database used by /robots endpoint
def insert_robot(robot_id: str, robot_name: str = None) -> None:
    if not robot_id:
        raise ValueError("Robot ID cannot be empty")
    created_at = datetime.now().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO robots (id, name, created_at) VALUES (?, ?, ?)",
        (robot_id, robot_name, created_at)
    )
    conn.commit()
    conn.close()


# Function to get all robots from the database used by /robots endpoint
def get_all_robots() -> list:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, created_at FROM robots")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "created_at": r[2]} for r in rows]

# Function to get a robot by ID used by /robots/{robot_id} endpoint
def get_robot_instructions(robot_id: str) -> list:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT blocks
        FROM instructions
        WHERE robot_id = ? AND is_completed = FALSE
        ORDER BY id ASC
        LIMIT 1
    """, (robot_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return [int(x) for x in row[0].split(",")]
    return []

# Function to mark an instruction as completed used by /instructions/complete endpoint
def insert_instruction(robot_id: str, blocks: list):
    valid_blocks = [2, 3, 6, 7, 10]
    if not all(b in valid_blocks for b in blocks):
        raise ValueError("Invalid block numbers. Only 2, 3, 6, 7, 10 are allowed.")
    blocks_str = ",".join(str(b) for b in blocks)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO instructions (robot_id, blocks) VALUES (?, ?)",
        (robot_id, blocks_str)
    )
    conn.commit()
    conn.close()
