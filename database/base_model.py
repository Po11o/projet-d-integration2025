from typing import Dict, Any, List
from .db_handler import DatabaseHandler

class BaseModel:
    table_name: str = ""
    db_handler: DatabaseHandler = None

    @classmethod
    def set_db_handler(cls, handler: DatabaseHandler):
        cls.db_handler = handler

    @classmethod
    def create(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {cls.table_name} ({columns}) VALUES ({placeholders})"
        
        return cls.db_handler.execute_query(query, tuple(data.values()))

    @classmethod
    def get_by_id(cls, id_value: Any) -> Dict[str, Any]:
        query = f"SELECT * FROM {cls.table_name} WHERE id = ?"
        results = cls.db_handler.execute_query(query, (id_value,))
        return results[0] if results else None

    @classmethod
    def get_all(cls) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM {cls.table_name}"
        return cls.db_handler.execute_query(query)

    @classmethod
    def update(cls, id_value: Any, data: Dict[str, Any]) -> None:
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {cls.table_name} SET {set_clause} WHERE id = ?"
        values = tuple(data.values()) + (id_value,)
        cls.db_handler.execute_query(query, values)

    @classmethod
    def delete(cls, id_value: Any) -> None:
        query = f"DELETE FROM {cls.table_name} WHERE id = ?"
        cls.db_handler.execute_query(query, (id_value,))