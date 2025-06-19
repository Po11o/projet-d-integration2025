from .db_handler import DatabaseHandler
from .base_model import BaseModel
from .db_init import init_db, DB_PATH
from .models import Robot, Instruction, Telemetry, Summary
from typing import List, Optional, Dict, Any
import sqlite3
from datetime import datetime

__all__ = [
    'DatabaseHandler',
    'BaseModel',
    'init_db',
    'DB_PATH',
    'Robot',
    'Instruction',
    'Telemetry',
    'Summary',
    'get_all_robots',
    'insert_robot',
    'get_robot_instructions',
    'insert_instruction',
    'get_robot_telemetry',
    'insert_telemetry',
    'get_robot_summary',
    'insert_summary'
]

# Initialize database handler
db_handler = DatabaseHandler(DB_PATH)
BaseModel.set_db_handler(db_handler)

def get_all_robots() -> List[Dict[str, Any]]:
    """Get all robots from database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, created_at FROM robots")
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "name": r[1], "created_at": r[2]} for r in rows]
    except Exception as e:
        logger.error(f"Error getting robots: {e}")
        raise

def insert_robot(robot_id: str, name: str) -> None:
    """Insert a new robot"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO robots (id, name) VALUES (?, ?)",
            (robot_id, name)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error inserting robot: {e}")
        raise

def get_robot_instructions(robot_id: str) -> Optional[List[int]]:
    """Get current instructions for a robot"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT blocks FROM instructions 
            WHERE robot_id = ? AND is_completed = FALSE 
            ORDER BY id DESC LIMIT 1
        """, (robot_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0]:
            return [int(x) for x in row[0].split(',')]
        return None
    except Exception as e:
        logger.error(f"Error getting instructions: {e}")
        raise

def insert_instruction(robot_id: str, blocks: List[int]) -> None:
    """Insert new instructions for a robot"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO instructions (robot_id, blocks)
            VALUES (?, ?)
        """, (robot_id, ','.join(map(str, blocks))))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error inserting instruction: {e}")
        raise

def get_robot_telemetry(robot_id: str) -> Optional[Dict[str, Any]]:
    """Get latest telemetry for a robot"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT speed, ultrasonic_distance, current_line, gripper_state, timestamp
            FROM telemetry WHERE robot_id = ?
            ORDER BY id DESC LIMIT 1
        """, (robot_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "speed": row[0],
                "ultrasonic_distance": row[1],
                "current_line": row[2],
                "gripper_state": row[3],
                "timestamp": row[4]
            }
        return None
    except Exception as e:
        logger.error(f"Error getting telemetry: {e}")
        raise

def insert_telemetry(robot_id: str, speed: float, distance: float, 
                    line: int, gripper: str) -> None:
    """Insert new telemetry data"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO telemetry 
            (robot_id, speed, ultrasonic_distance, current_line, gripper_state)
            VALUES (?, ?, ?, ?, ?)
        """, (robot_id, speed, distance, line, gripper))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error inserting telemetry: {e}")
        raise

def get_robot_summary(robot_id: str) -> Optional[Dict[str, Any]]:
    """Get latest summary for a robot"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT average_speed, timestamp
            FROM summary WHERE robot_id = ?
            ORDER BY id DESC LIMIT 1
        """, (robot_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "average_speed": row[0],
                "timestamp": row[1]
            }
        return None
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        raise

def insert_summary(robot_id: str, average_speed: float) -> None:
    """Insert new summary data"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO summary (robot_id, average_speed)
            VALUES (?, ?)
        """, (robot_id, average_speed))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error inserting summary: {e}")
        raise