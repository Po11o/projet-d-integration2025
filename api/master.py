# master.py
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from __init__ import initialize
from routes import router

app = FastAPI(title="Robot Control API")

# Mount static files & templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Include all of our application routes
app.include_router(router)

# Initialize DB & default data
initialize()

if __name__ == "__main__":
    uvicorn.run("master:app", host="0.0.0.0", port=8000, reload=True)
