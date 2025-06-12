from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
import uvicorn
import logging
import sqlite3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from database import (
    init_db,
    get_all_robots,
    insert_robot,
    insert_instruction,
    get_robot_instructions,
    DB_PATH
)

app = FastAPI(title="Robot Control API")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize DB
try:
    init_db()
    logger.info("Database initialized successfully")
    if not get_all_robots():
        insert_robot("REF-01")
        logger.info("Default robot REF-01 created")
except Exception as e:
    logger.error(f"Database initialization failed: {e}")
    raise

# Pydantic models
class RobotIn(BaseModel):
    robot_id: str

class InstructionIn(BaseModel):
    robot_id: str
    blocks: List[int]

class SummaryIn(BaseModel):
    robot_id: str
    average_speed: float

# Routes
# Root endpoint serving the web UI
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    try:
        robots = get_all_robots()
        return templates.TemplateResponse("index.html", {"request": request, "robots": robots})
    except Exception as e:
        logger.error(f"Error in index: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to list all robots
@app.get("/robots/list")
async def list_robots():
    try:
        return get_all_robots()
    except Exception as e:
        logger.error(f"Error listing robots: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to create a new robot
@app.post("/robots")
async def create_robot(robot: RobotIn):
    if not robot.robot_id:
        raise HTTPException(status_code=400, detail="Robot ID is required")
    try:
        insert_robot(robot.robot_id)
        return RedirectResponse(url="/", status_code=303)
    except ValueError as ve:
        logger.warning(f"Invalid robot data: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error creating robot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to create a new instruction
@app.post("/instructions")
async def create_instruction(inst: InstructionIn):
    try:
        insert_instruction(inst.robot_id, inst.blocks)
        return RedirectResponse(url="/", status_code=303)
    except ValueError as ve:
        logger.warning(f"Invalid instruction data: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error creating instruction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to get the next instruction for a robot
@app.get("/instructions")
async def read_instruction(robot_id: str):
    try:
        blocks = get_robot_instructions(robot_id)
        return {"blocks": blocks}
    except Exception as e:
        logger.error(f"Error reading instructions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to list all instructions for logging purposes
@app.get("/instructions/all")
async def list_all_instructions():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT robot_id, blocks, is_completed
            FROM instructions
            ORDER BY id DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "robot_id": r[0],
                "blocks": [int(x) for x in r[1].split(",")],
                "is_completed": bool(r[2])
            }
            for r in rows
        ]
    except Exception as e:
        logger.error(f"Error listing all instructions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to update telemetry data from the robot 
# currently only recieves data from robot_simulator.py until the robot is finalized.
@app.post("/telemetry")
async def update_telemetry(request: Request):
    try:
        data = await request.json()
        required = ['robot_id', 'speed', 'ultrasonic_distance', 'current_line', 'gripper_state']
        for field in required:
            if field not in data:
                raise HTTPException(status_code=400, detail=f"Missing field: {field}")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO telemetry
            (robot_id, speed, ultrasonic_distance, current_line, gripper_state)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data["robot_id"],
            data["speed"],
            data["ultrasonic_distance"],
            data["current_line"],
            data["gripper_state"]
        ))
        conn.commit()
        conn.close()
        return {"status": "ok"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating telemetry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to get the latest telemetry data for a robot
@app.get("/telemetry")
async def get_latest_telemetry(robot_id: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT speed, ultrasonic_distance, current_line, gripper_state, time_stamp
            FROM telemetry
            WHERE robot_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (robot_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return {}
        return {
            "speed": row[0],
            "ultrasonic_distance": row[1],
            "current_line": row[2],
            "gripper_state": row[3],
            "time_stamp": row[4],
        }
    except Exception as e:
        logger.error(f"Error fetching telemetry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to get the telemetry history for a robot
@app.get("/telemetry/all")
async def get_telemetry_history(robot_id: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT speed, ultrasonic_distance, current_line, gripper_state, time_stamp
            FROM telemetry
            WHERE robot_id = ?
            ORDER BY id DESC
        """, (robot_id,))
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "speed": r[0],
                "ultrasonic_distance": r[1],
                "current_line": r[2],
                "gripper_state": r[3],
                "time_stamp": r[4],
            }
            for r in rows
        ]
    except Exception as e:
        logger.error(f"Error fetching telemetry history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to create a summary of robot performance
@app.post("/summary")
async def create_summary(summary: SummaryIn):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO summary
              (robot_id, average_speed)
            VALUES (?, ?)
        """, (summary.robot_id, summary.average_speed))
        conn.commit()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error saving summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to get the latest summary for a robot
@app.get("/summary")
async def get_all_summaries(robot_id: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT average_speed, time_stamp
            FROM summary
            WHERE robot_id = ?
            ORDER BY id DESC
        """, (robot_id,))
        rows = cursor.fetchall()
        conn.close()

        # Return a list of all summaries
        return [
            {"average_speed": r[0], "time_stamp": r[1]}
            for r in rows
        ]
    except Exception as e:
        logger.error(f"Error fetching summaries: {e}")
        raise HTTPException(status_code=500, detail=str(e))
# a simple test api that returns "success when invoked"
@app.get("/test")
async def test_api():
    return {"status": "success"}

# Startup event to log available endpoints (debug purposes, temporary)
@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI server starting up")
    logger.info("Available endpoints:")
    logger.info("  GET    /                  - Web UI")
    logger.info("  GET    /robots/list       - List robots")
    logger.info("  POST   /robots            - Add robot")
    logger.info("  POST   /instructions      - Add  instruction")
    logger.info("  GET    /instructions      - Next instruction")
    logger.info("  GET    /instructions/all  - All instructions")
    logger.info("  POST   /telemetry         - Push telemetry")
    logger.info("  GET    /telemetry         - Latest telemetry")
    logger.info("  GET    /telemetry/all     - Telemetry history")
    logger.info("  POST   /summary           - Push summary")
    logger.info("  GET    /summary           - Latest summary")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
