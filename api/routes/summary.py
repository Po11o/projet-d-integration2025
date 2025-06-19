from fastapi import APIRouter, HTTPException
from database.models import Summary
from ..models.schemas import SummaryIn

router = APIRouter()

@router.post("/")
async def create_summary(summary: SummaryIn):
    try:
        Summary.create_summary(
            robot_id=summary.robot_id,
            average_speed=summary.average_speed
        )
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{robot_id}")
async def get_summary(robot_id: str):
    try:
        data = Summary.get_latest_for_robot(robot_id)
        return data if data else {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))