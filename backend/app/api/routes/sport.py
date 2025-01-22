from typing import Union

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from db.session import get_db_connection

router = APIRouter()


class Workout(BaseModel):
    telegram_id: int
    type: str
    duration: int
    calories: int
    water_spent: Union[float, int]
    temperature: float


@router.post("/log_workout")
async def log_workout(workout: Workout):
    conn = await get_db_connection()
    try:
        await conn.execute(
            """
            INSERT INTO workout_log (telegram_id, type, duration, calories, temperature, water_spent)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            workout.telegram_id, workout.type, workout.duration, workout.calories,
            workout.temperature, workout.water_spent
        )
        return {"message": "Workout logged successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await conn.close()


@router.get("/check_today_workouts/{telegram_id}")
async def check_today_workouts(telegram_id: int):
    conn = await get_db_connection()
    try:
        total_time = await conn.fetch(
            """
            SELECT SUM(duration) as total_time
            FROM workout_log
            WHERE DATE_TRUNC('day', event_time) = DATE_TRUNC('day', now())
                AND telegram_id = $1
            """,
            telegram_id
        )
        total_time = total_time[0].get('total_time')

        total_calories = await conn.fetch(
            """
            SELECT SUM(calories) as total_calories
            FROM workout_log
            WHERE DATE_TRUNC('day', event_time) = DATE_TRUNC('day', now())
                AND telegram_id = $1
            """,
            telegram_id
        )
        total_calories = total_calories[0].get('total_calories')

        total_water = await conn.fetch(
            """
            SELECT SUM(water_spent) as total_calories
            FROM workout_log
            WHERE DATE_TRUNC('day', event_time) = DATE_TRUNC('day', now())
                AND telegram_id = $1
            """,
            telegram_id
        )
        total_water = total_water[0].get('total_calories')

        result = {
            'total_time': total_time,
            'total_calories': total_calories,
            'total_water': total_water
        }

        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await conn.close()
