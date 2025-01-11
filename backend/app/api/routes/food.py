from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from db.session import get_db_connection

router = APIRouter()


class NewFood(BaseModel):
    telegram_id: int
    food_name: str
    food_weight: float
    calories: float


@router.post("/log_food")
async def log_food(food: NewFood):
    conn = await get_db_connection()
    try:
        await conn.execute(
            """
            INSERT INTO food_log (telegram_id, food_name, weight, calories)
            VALUES ($1, $2, $3, $4)
            """,
            food.telegram_id, food.food_name, food.food_weight, food.calories
        )
        return {"message": "Food logged successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await conn.close()
