from fastapi import APIRouter, HTTPException
from database.models import Telemetry
from ..models.schemas import TelemetryIn

router = APIRouter()

@router.post("/")
async def update_telemetry(telemetry: TelemetryIn):
    try:
        Telemetry.create_entry(
            robot_id=telemetry.robot_id,
            speed=telemetry.vitesse,
            distance=telemetry.distance_ultrasons,
            line=telemetry.ligne,
            gripper=telemetry.statut_pince
        )
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{robot_id}")
async def get_telemetry(robot_id: str):
    try:
        data = Telemetry.get_latest_for_robot(robot_id)
        return data if data else {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))