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


@router.get("/check_today_intake/{telegram_id}")
async def check_today_intake(telegram_id: int):
    conn = await get_db_connection()
    try:
        total_calories = await conn.fetch(
            """
            SELECT SUM(calories) as total_calories
            FROM food_log
            WHERE DATE_TRUNC('day', event_time) = DATE_TRUNC('day', now())
                AND telegram_id = $1
            """,
            telegram_id
        )
        total_calories = total_calories[0].get('total_calories')

        calories_by_food = await conn.fetch(
            """
            SELECT food_name, SUM(calories) as calories
            FROM food_log
            WHERE DATE_TRUNC('day', event_time) = DATE_TRUNC('day', now())
                AND telegram_id = $1
            GROUP BY food_name
            """,
            telegram_id
        )

        result = {
            'total_calories': total_calories,
            'calories_by_food': calories_by_food
        }

        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await conn.close()
