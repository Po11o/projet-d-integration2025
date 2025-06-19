from pydantic import BaseModel
from typing import List

class RobotIn(BaseModel):
    robot_id: str
    name: str

class InstructionIn(BaseModel):
    robot_id: str
    blocks: List[int]

class TelemetryIn(BaseModel):
    robot_id: str
    vitesse: float
    distance_ultrasons: float
    statut_deplacement: str
    ligne: int
    statut_pince: str

class SummaryIn(BaseModel):
    robot_id: str
    average_speed: float