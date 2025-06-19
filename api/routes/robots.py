from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from database.models import Robot
from ..models.schemas import RobotIn

router = APIRouter()

@router.get("/list")
async def list_robots():
    try:
        return Robot.get_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_robot(request: Request):
    try:
        form = await request.form()
        robot_id = form.get("robot_id")
        name = form.get("name")
        if not robot_id or not name:
            raise HTTPException(status_code=400, detail="Robot ID and name required")
        Robot.create_with_name(robot_id, name)
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))