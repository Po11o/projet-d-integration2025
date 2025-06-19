from typing import List, Optional
from datetime import datetime
from .base_model import BaseModel

class Robot(BaseModel):
    table_name = "robots"

    @classmethod
    def create_with_name(cls, robot_id: str, name: str) -> dict:
        return cls.create({
            "id": robot_id,
            "name": name,
            "created_at": datetime.now().isoformat()
        })

class Instruction(BaseModel):
    table_name = "instructions"

    @classmethod
    def create_for_robot(cls, robot_id: str, blocks: List[int]) -> dict:
        return cls.create({
            "robot_id": robot_id,
            "blocks": ",".join(map(str, blocks)),
            "is_completed": False
        })

    @classmethod
    def get_active_for_robot(cls, robot_id: str) -> Optional[dict]:
        query = """
            SELECT * FROM instructions 
            WHERE robot_id = ? AND is_completed = FALSE 
            ORDER BY id DESC LIMIT 1
        """
        results = cls.db_handler.execute_query(query, (robot_id,))
        return results[0] if results else None

class Telemetry(BaseModel):
    table_name = "telemetry"

    @classmethod
    def create_entry(cls, robot_id: str, speed: float, distance: float, 
                    line: int, gripper: str) -> dict:
        return cls.create({
            "robot_id": robot_id,
            "speed": speed,
            "ultrasonic_distance": distance,
            "current_line": line,
            "gripper_state": gripper,
            "timestamp": datetime.now().isoformat()
        })

class Summary(BaseModel):
    table_name = "summary"

    @classmethod
    def create_summary(cls, robot_id: str, avg_speed: float) -> dict:
        return cls.create({
            "robot_id": robot_id,
            "average_speed": avg_speed,
            "timestamp": datetime.now().isoformat()
        })