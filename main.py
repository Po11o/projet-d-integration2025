from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel


from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from database import (
    init_db,
    get_all_robots,
    get_all_movements,
    insert_movement,
    insert_robot
)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database setup
init_db()
if not get_all_robots():
    insert_robot("REF-01", "Model-X")

# Pydantic model
class Movement(BaseModel):
    robot_id: int
    action: str

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    robots = get_all_robots()
    movements = get_all_movements()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "robots": robots,
        "movements": movements
    })

@app.post("/movement")
async def receive_movement(m: Movement):
    insert_movement(m.robot_id, m.action)
    return {
        "status": "ok",
        "message": f"Action '{m.action}' recorded for robot ID {m.robot_id}"
    }

@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {
        "request": request,
        "id": id
    })
@app.get("/movements")
async def get_movements():
    return get_all_movements()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
