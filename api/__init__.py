# init.py
import logging
from database import init_db, get_all_robots, insert_robot

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def initialize():
    """
    Initialize the database and seed a default robot if none exist.
    """
    init_db()
    if not get_all_robots():
        insert_robot("REF-01", "Reference Bot")
        logger.info("Default robot REF-01 created with name 'Reference Bot'")

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Create FastAPI instance
app = FastAPI(title="Robot Control API")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Import routes after app creation
from .routes import api_router
app.include_router(api_router, prefix="/api")

# Initialize database
from database import init_db
init_db()