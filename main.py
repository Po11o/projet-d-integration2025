from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional

from database import (
    init_db,
    get_all_robots,
    get_all_missions,
    get_all_statut_robot,
    insert_robot,
    insert_mission,
    insert_statut_robot,
)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database setup
init_db()
if not get_all_robots():
    insert_robot("REF-01")

# Pydantic models
class RobotStatus(BaseModel):
    robot_id: str
    position: str
    horodatage: str
    etat: str

class MissionIn(BaseModel):
    robot_id: str
    cube: int

class MissionRequest(BaseModel):
    robot_id: str
    mission_id: Optional[int] = None
    done: Optional[bool] = False

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    robots = get_all_robots()
    missions = get_all_missions()
    status = get_all_statut_robot()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "robots": robots,
        "missions": missions,
        "status": status
    })

@app.post("/robot_status")
async def robot_status(status: RobotStatus):
    robots = get_all_robots()
    if not any(r["id"] == status.robot_id for r in robots):
        raise HTTPException(status_code=404, detail="Robot not found")
    insert_statut_robot(status.robot_id, status.position, status.horodatage, status.etat)
    return {"status": "ok"}

@app.post("/mission")
async def add_mission(mission: MissionIn):
    robots = get_all_robots()
    if not any(r["id"] == mission.robot_id for r in robots):
        raise HTTPException(status_code=404, detail="Robot not found")
    insert_mission(mission.robot_id, mission.cube, "à_faire")
    return {"status": "ok"}

@app.post("/next_mission")
async def next_mission(req: MissionRequest):
    import sqlite3
    DB_PATH = "data/robots.db"
    # Mark previous mission as done if needed
    if req.mission_id and req.done:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE missions SET etat='terminé' WHERE id=? AND robot_id=?", (req.mission_id, req.robot_id))
        conn.commit()
        conn.close()
    # Get next mission
    missions = get_all_missions()
    for m in missions:
        if m["robot_id"] == req.robot_id and m["etat"] == "à_faire":
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("UPDATE missions SET etat='en_cours' WHERE id=?", (m["id"],))
            conn.commit()
            conn.close()
            return {"mission_id": m["id"], "cube": m["cube"]}
    return {"mission_id": None, "cube": None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)