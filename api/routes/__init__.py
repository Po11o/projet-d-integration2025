from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database import (
    get_all_robots,
    insert_robot,
    insert_instruction,
    get_robot_instructions,
    DB_PATH
)
from ..models.schemas import RobotIn, InstructionIn, SummaryIn
import sqlite3
import logging

logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="templates")
api_router = APIRouter()

# Web Routes
@api_router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@api_router.get("/partials/{partial_name}", response_class=HTMLResponse)
async def get_partial(request: Request, partial_name: str):
    context = {"request": request}
    
    if partial_name == "active":
        robots = get_all_robots()
        instructions = {r["id"]: get_robot_instructions(r["id"]) or ["None"] for r in robots}
        context.update({"robots": robots, "instructions": instructions})
    
    elif partial_name == "history":
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
        context["history"] = [
            {
                "robot_id": r[0],
                "robot_name": r[1],
                "blocks": [int(x) for x in r[2].split(",")],
                "is_completed": bool(r[3])
            }
            for r in rows
        ]
    
    elif partial_name == "telemetry":
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
        context.update({"robots": robots, "telemetry": telemetry})
    
    elif partial_name == "summary":
        robots = get_all_robots()
        summary = {}
        for r in robots:
            rid = r["id"]
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                SELECT timestamp FROM summary 
                WHERE robot_id = ? ORDER BY id DESC LIMIT 1
            """, (rid,))
            rows = cur.fetchall()
            conn.close()
            summary[rid] = [{"time_stamp": t[0]} for t in rows]
        context.update({"robots": robots, "summary": summary})
    
    elif partial_name == "robots":
        return templates.TemplateResponse("partials/robots_add.html", context)

    return templates.TemplateResponse(f"partials/{partial_name}.html", context)

# Robot Routes
@api_router.get("/robots/list")
async def list_robots():
    try:
        return get_all_robots()
    except Exception as e:
        logger.error(f"Error listing robots: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/robots")
async def create_robot(request: Request):
    try:
        form = await request.form()
        robot_id = form.get("robot_id")
        name = form.get("name")
        if not robot_id or not name:
            raise HTTPException(status_code=400, detail="Robot ID and name required")
        insert_robot(robot_id, name)
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        logger.error(f"Error creating robot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Instruction Routes
@api_router.post("/instructions/create")
async def create_instruction(inst: InstructionIn):
    try:
        insert_instruction(inst.robot_id, inst.blocks)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/instructions")
async def read_instruction(robot_id: str):
    if not robot_id:
        raise HTTPException(status_code=400, detail="Robot ID required")
    try:
        return {"blocks": get_robot_instructions(robot_id) or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Remove the existing reset endpoints and replace with a single one
@api_router.post("/reset")
async def reset_instructions(robot_id: str = None):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        if robot_id:
            # Reset for specific robot
            cur.execute("""
                DELETE FROM instructions 
                WHERE robot_id = ? AND is_completed = 0
            """, (robot_id,))
        else:
            # Reset all robots
            cur.execute("DELETE FROM instructions WHERE is_completed = 0")
        
        affected = cur.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"Deleted {affected} instructions" + (f" for robot {robot_id}" if robot_id else ""))
        
        # If called from web form, redirect back to history
        if not robot_id:
            return RedirectResponse(url="/", status_code=303)
            
        return {
            "status": "ok",
            "message": f"Deleted {affected} instructions" + (f" for robot {robot_id}" if robot_id else "")
        }
            
    except Exception as e:
        logger.error(f"Error deleting instructions: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to delete instructions: {str(e)}"
        )

# Telemetry Routes
@api_router.post("/telemetry")
async def update_telemetry(request: Request):
    data = await request.json()
    required = ["robot_id", "vitesse", "distance_ultrasons", 
                "statut_deplacement", "ligne", "statut_pince"]
    for f in required:
        if f not in data:
            raise HTTPException(status_code=400, detail=f"Missing field: {f}")
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO telemetry 
               (robot_id, speed, ultrasonic_distance, displacement_status, 
                current_line, gripper_state)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (data["robot_id"], data["vitesse"], data["distance_ultrasons"],
             data["statut_deplacement"], data["ligne"], data["statut_pince"])
        )
        conn.commit()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Summary Routes
@api_router.post("/summary")
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
        conn.commit()
        conn.close()
        return {"status": "ok", "instruction_completed": bool(row)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))