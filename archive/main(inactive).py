import os
import sqlite3
import logging
from datetime import datetime
from typing import List

from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from database import (
    init_db,
    get_all_robots,
    insert_robot,
    insert_instruction,
    get_robot_instructions,
    DB_PATH
)
from api.routes import api_router

# ——— Logging ———
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ——— FastAPI setup ———
app = FastAPI(
    title="Robot Control API",
    description="Pathfinder Robot Control and Monitoring System",
    version="1.0.0"
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Include API routes
app.include_router(api_router)

# ——— Initialize DB & seed ———
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing application...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

# ——— Pydantic models ———
class RobotIn(BaseModel):
    robot_id: str
    name: str

class InstructionIn(BaseModel):
    robot_id: str
    blocks: List[int]

class SummaryIn(BaseModel):
    robot_id: str

# ——— Root: main HTML dashboard with iframes ———
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ——— Partials ———
@app.get("/partials/active", response_class=HTMLResponse)
async def partial_active(request: Request):
    robots = get_all_robots()
    instructions = {r["id"]: get_robot_instructions(r["id"]) or ["None"] for r in robots}
    return templates.TemplateResponse("partials/active.html", {
        "request": request,
        "robots": robots,
        "instructions": instructions,
    })

@app.get("/partials/history", response_class=HTMLResponse)
async def partial_history(request: Request):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT i.robot_id, r.name, i.blocks, i.is_completed 
        FROM instructions i
        JOIN robots r ON i.robot_id = r.id 
        ORDER BY i.id DESC
    """)
    rows = cur.fetchall()
    conn.close()
    history = [
        {
            "robot_id": r[0],
            "robot_name": r[1],
            "blocks": [int(x) for x in r[2].split(",")],
            "is_completed": bool(r[3])
        }
        for r in rows
    ]
    return templates.TemplateResponse("partials/history.html", {
        "request": request, 
        "history": history
    })

@app.get("/partials/telemetry", response_class=HTMLResponse)
async def partial_telemetry(request: Request):
    robots = get_all_robots()
    telemetry = {}
    for r in robots:
        rid = r["id"]
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
          SELECT speed, ultrasonic_distance, current_line, gripper_state, time_stamp
          FROM telemetry WHERE robot_id=? ORDER BY id DESC
        """, (rid,))
        rows = cur.fetchall()
        conn.close()
        telemetry[rid] = [
            {"speed": s, "ultrasonic_distance": d, "current_line": l,
             "gripper_state": g, "time_stamp": t}
            for s, d, l, g, t in rows
        ]
    return templates.TemplateResponse("partials/telemetry.html", {
        "request": request,
        "robots": robots,
        "telemetry": telemetry,
    })

@app.get("/partials/summary", response_class=HTMLResponse)
async def partial_summary(request: Request):
    robots = get_all_robots()  # This now returns both id and name
    summary = {}
    for r in robots:
        rid = r["id"]
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            SELECT s.timestamp 
            FROM summary s
            WHERE s.robot_id = ? 
            ORDER BY s.id DESC
        """, (rid,))
        rows = cur.fetchall()
        conn.close()
        summary[rid] = [{"time_stamp": t[0]} for t in rows]
    return templates.TemplateResponse("partials/summary.html", {
        "request": request,
        "robots": robots,  # Contains both id and name
        "summary": summary,
    })

@app.get("/partials/robots", response_class=HTMLResponse)
async def partial_robots(request: Request):
    return templates.TemplateResponse("partials/robots_add.html", {"request": request})

# ——— JSON API endpoints ———
@app.get("/robots/list")
async def list_robots():
    try:
        return get_all_robots()
    except Exception as e:
        logger.error(f"Error listing robots: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/robots")
async def create_robot(request: Request):
    try:
        form = await request.form()
        robot_id = form.get("robot_id")
        name = form.get("name")
        if not robot_id or not name:
            raise HTTPException(status_code=400, detail="Robot ID and name are required")
        insert_robot(robot_id, name)
        return RedirectResponse(url="/", status_code=303)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error creating robot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/instructions/create")
async def create_instruction(inst: InstructionIn):
    try:
        insert_instruction(inst.robot_id, inst.blocks)
        return RedirectResponse(url="/", status_code=303)
    except ValueError as ve:
        raise HTTPException(400, str(ve))
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/instructions")
async def read_instruction(robot_id: str):
    if not robot_id:
        raise HTTPException(400, "Robot ID is required")
    try:
        return {"blocks": get_robot_instructions(robot_id) or []}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/instructions/all")
async def list_all_instructions():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT robot_id, blocks, is_completed FROM instructions ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()
        return [
            {"robot_id": r0, "blocks": [int(x) for x in r1.split(",")], "is_completed": bool(r2)}
            for r0, r1, r2 in rows
        ]
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/telemetry")
async def update_telemetry(request: Request):
    data = await request.json()
    required = ["robot_id", "vitesse", "distance_ultrasons", "statut_deplacement", "ligne", "statut_pince"]
    for f in required:
        if f not in data:
            raise HTTPException(400, f"Missing field: {f}")
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO telemetry (robot_id, speed, ultrasonic_distance, displacement_status, current_line, gripper_state) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (data["robot_id"], data["vitesse"], data["distance_ultrasons"],
             data["statut_deplacement"], data["ligne"], data["statut_pince"])
        )
        conn.commit(); conn.close()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/summary")
async def create_summary(summary: SummaryIn):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # Find and mark earliest uncompleted instruction
        cur.execute("""
            SELECT id FROM instructions
            WHERE robot_id = ? AND is_completed = 0
            ORDER BY id ASC LIMIT 1
        """, (summary.robot_id,))
        row = cur.fetchone()

        if row:
            cur.execute("UPDATE instructions SET is_completed = 1 WHERE id = ?", (row[0],))

        # Insert summary timestamp
        cur.execute("INSERT INTO summary (robot_id) VALUES (?)", (summary.robot_id,))
        conn.commit(); conn.close()
        return {"status": "ok", "instruction_completed": bool(row)}
    except Exception as e:
        raise HTTPException(500, str(e))

# ——— Validation handler ———
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(400, {"detail": "Invalid JSON or missing fields."})
