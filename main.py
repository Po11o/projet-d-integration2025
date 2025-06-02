from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import asyncio
from database import init_db, get_all_robots, insert_robot

app = FastAPI()

init_db()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/robots")
async def api_get_robots():
    return get_all_robots()

# 🔄 Background task: insert new robot every 5 seconds
async def add_robot_forever():
    count = 1
    while True:
        name = f"AutoBot{count}"
        model = "REF-AUTO"
        print(f"➕ Inserting robot: {name}")
        insert_robot(name, model)
        count += 1
        await asyncio.sleep(5)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(add_robot_forever())
