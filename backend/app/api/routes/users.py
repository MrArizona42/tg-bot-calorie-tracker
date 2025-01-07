from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from db.session import get_db_connection

router = APIRouter()


class UserCreate(BaseModel):
    telegram_id: int
    name: str
    age: int
    weight: float
    city: str
    target_active_minutes_per_day: int
    target_calories_per_day: int


@router.post("/register_user")
async def create_user(user: UserCreate):
    conn = await get_db_connection()
    try:
        await conn.execute(
            """
            INSERT INTO users (telegram_id, name, age, weight, city, target_active_minutes_per_day, target_calories_per_day)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            user.telegram_id, user.name, user.age, user.weight, user.city,
            user.target_active_minutes_per_day, user.target_calories_per_day
        )
        return {"message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await conn.close()
