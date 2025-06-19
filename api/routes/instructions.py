from fastapi import APIRouter, HTTPException
from api.models.schemas import InstructionIn
from database import get_robot_instructions, insert_instruction

router = APIRouter()

@router.get("/")
async def get_instructions(robot_id: str):
    try:
        blocks = get_robot_instructions(robot_id)
        return {"blocks": blocks or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create")
async def create_instruction(inst: InstructionIn):
    try:
        insert_instruction(inst.robot_id, inst.blocks)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))